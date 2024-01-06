# sightwire, Apache-2.0 license
# Filename: convertors/lcm.py
# Description:  LCM logs conversion courtesy K. Barnard. Replaced argparse with click and restyled.
from typing import List
import pandas as pd
from pathlib import Path
from datetime import datetime

from sightwire.logger import info


def convert_timestamp_to_datetime_10(timestamp: str) -> datetime:
    """
    Convert a timestamp string, e.g. "1699643617" to a datetime object
    :param timestamp:
    :return:  datetime object
    """
    return datetime.fromtimestamp(float(timestamp))


def convert_timestamp_to_datetime_16(timestamp: str) -> datetime:
    """
    Convert a timestamp string, e.g. "1699643617662483" to a datetime object
    :param timestamp:
    :return:  datetime object
    """
    seconds = float(str(timestamp)[0:10]) + float(str(timestamp)[10:]) / 1e6
    return datetime.fromtimestamp(seconds)


def search_nearest(depth_log: Path, position_log: Path, image_list: List[Path], max_images: int) -> pd.DataFrame:
    """
    Find the nearest depth and position for a given image or a pair of images
    :param image_list: Path to the image list file
    :param depth_log: Path to the depth log file
    :param position_log:  Path to the position log file
    :param max_images:  Maximum number of images to process
    :return:
    """
    if len(image_list) == 0:
        info(f'No images found in {image_list}')
        assert False

    # Combine the images into a single dataframe
    left_images = [item for item in image_list if "_LEFT" in item.as_posix() or "_L" in item.as_posix()]
    right_images = [item for item in image_list if "_RIGHT" in item.as_posix() or "_R" in item.as_posix()]

    stereo = False
    if len(left_images) > 0 and len(right_images) > 0:
        info(f'Found {len(left_images)} left images and {len(right_images)} right images')
        stereo = True
        # Assume the timestamp is in the filename, e.g. 1699643617662483 or 1699643617.662483
        if len(left_images[0].stem) == 10:
            df_left = pd.DataFrame({'left': left_images})
            df_left['iso_datetime'] = df_left['left'].apply(lambda x: convert_timestamp_to_datetime_10(x.stem))
            df_right = pd.DataFrame({'right': right_images})
            df_right['iso_datetime'] = df_right['right'].apply(lambda x: convert_timestamp_to_datetime_10(x.stem))
        else:
            df_left = pd.DataFrame({'left': left_images})
            df_left['iso_datetime'] = df_left['left'].apply(lambda x: convert_timestamp_to_datetime_16(x.stem))
            df_right = pd.DataFrame({'right': right_images})
            df_right['iso_datetime'] = df_right['right'].apply(lambda x: convert_timestamp_to_datetime_16(x.stem))
    else:
        info(f'Found {len(image_list)} images')
        if len(image_list[0].stem) == 10:
            df = pd.DataFrame({'image': image_list})
            df['iso_datetime'] = df['image'].apply(lambda x: convert_timestamp_to_datetime_10(x.stem))
        else:
            df = pd.DataFrame({'image': image_list})
            df['iso_datetime'] = df['image'].apply(lambda x: convert_timestamp_to_datetime_16(x.stem))

    if stereo:
        # Allow time difference tolerance (600 milliseconds) for the nearest depth and position between the left and
        # right images
        tolerance = pd.Timedelta('600ms')
        df = pd.merge_asof(df_left, df_right, on='iso_datetime', direction='nearest', tolerance=tolerance)
        df.sort_values(by=['iso_datetime'], inplace=True)
        df.reset_index(inplace=True)

    # Limit the number of images to process
    if max_images > 0:
        df = df.head(max_images)

    # Add columns for depth and position
    df['longitude'] = None
    df['latitude'] = None
    df['depth'] = None

    # Replace Path objects with strings
    if stereo:
        df['left'] = df['left'].apply(lambda x: x.as_posix())
        df['right'] = df['right'].apply(lambda x: x.as_posix())
    else:
        df['image'] = df['image'].apply(lambda x: x.as_posix())

    df_depth = pd.read_csv(depth_log.as_posix())
    df_depth['lcm_timestamp'] = df_depth['lcm_timestamp'].apply(convert_timestamp_to_datetime_16)
    df_depth.sort_index(inplace=True)

    df_position = pd.read_csv(position_log.as_posix())
    df_position['lcm_timestamp'] = df_position['lcm_timestamp'].apply(convert_timestamp_to_datetime_16)
    df_position.sort_index(inplace=True)

    # For each image or image pair, find the closest depth and position by timestamp
    latitude = []
    longitude = []
    depth = []
    for key, value in sorted(df.iterrows()):
        depth_time_diff = abs(df_depth['lcm_timestamp'] - value.iso_datetime)
        position_time_diff = abs(df_position['lcm_timestamp'] - value.iso_datetime)
        closest_depth = df_depth.iloc[depth_time_diff.idxmin()]
        closest_position = df_position.iloc[position_time_diff.idxmin()]

        if stereo:
            info(
                f'image: {value.left} {value.right} lcm depth: {closest_depth.lcm_timestamp.timestamp()} {closest_depth.depth:.2f}')
            info(
                f'image: {value.left} {value.right} lcm position: {closest_position.lcm_timestamp.timestamp()} {closest_position.latitude:.2f} {closest_position.longitude:.2f}')
        else:
            info(f'image: {value.image} lcm depth: {closest_depth.lcm_timestamp.timestamp()} {closest_depth.depth:.2f}')
            info(
                f'image: {value.image} lcm position: {closest_position.lcm_timestamp.timestamp()} {closest_position.latitude:.2f} {closest_position.longitude:.2f}')

        longitude.append(closest_position.longitude)
        latitude.append(closest_position.latitude)
        depth.append(closest_depth.depth)

    df['longitude'] = longitude
    df['latitude'] = latitude
    df['depth'] = depth

    return df
