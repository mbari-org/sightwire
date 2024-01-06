# sightwire, Apache-2.0 license
# Filename: loaders/commands.py
# Description: Load stereo images, stereo video, metadata, and localization into the database
from datetime import datetime

import cv2
import numpy as np
import tempfile

import click
from pathlib import Path

import tator
from tator.util import make_multi_stream

from sightwire.converters.time_utils import search_nearest
from sightwire.database.common import init_api_project
from sightwire.logger import info, err
from sightwire.database.data_types import VideoData, Platform, ImageData, StereoImageData, Camera
from sightwire.database.common import find_media_type
from sightwire.database.media import create_video, create_image, create_stereo_image
from sightwire import common_args



@click.command("video", help="Load video into the database")
@common_args.host
@common_args.token
@common_args.project
@common_args.force
@click.option("--input", '-i', type=str, help='path to the video directory, or a single video file')
@click.option("--platform-type", type=Platform, default=Platform.MINI_ROV, required=True)
@click.option("--mission-name", type=str, required=True)
@click.option("--camera-type", type=Camera, default=Camera.FLIR, required=True)
def load_video(input: str, host: str, token: str, project: str, platform_type: Platform, mission_name: str,
               camera_type: Camera, force: bool):
    """
    Load video from a local file system to the database
    :param input: Absolute path to the video to load
    :param host: Hostname, e.g. localhost
    :param token: Authentication token
    :param project: Project name to load to
    :param platform_type: Platform type
    :param camera_type: Camera type
    :param force: True to force load and skip over check
    :param start_time: Start time of the video in ISO format, e.g. 2021-01-01T00:00:00
    :param end_time: End time of the video in ISO format, e.g. 2021-01-01T00:00:00
    :return:
    """
    video_path = Path(input)

    api, tator_project = init_api_project(host, token, project)

    media_type = find_media_type(api, tator_project.id, "Video")

    # If this is a directory, scan all the mp4 recursively
    if video_path.is_dir():
        video_to_load = sorted(video_path.rglob("*.mp4"))
    else:
        video_to_load = [video_path]

    info(f'Found {len(video_to_load)} media file to load')
    if force or click.confirm('Are you sure you want to load this media file?'
                              'You may want to check the database first to see if it is are already '
                              'loaded. Add --force to load anyway.'):
        for f in video_to_load:
            info(f'Uploading {f}')

            section = f'VID/{platform_type.name}/{camera_type.name}/{mission_name}'

            attribute_filter = [f'platform::{platform_type.name}', f'mission::{mission_name}',
                                f'camera::{camera_type.name}']

            # Search for media to get the start and end times
            media = api.get_media_list(tator_project.id, attribute=attribute_filter)

            # Remove any media that has the 'LEFT' or 'RIGHT' in the name
            # Can remove this if we drop the load of single images
            media = [m for m in media if 'LEFT' not in m.name and 'RIGHT' not in m.name]

            # Get the start and end time of the media
            if len(media) == 0:
                err(f'Could not find related media {f.name} with filter {attribute_filter}')
                raise FileNotFoundError
            else:
                media_data = api.get_media(media[0].id)
                start_time = datetime.fromisoformat(media_data.attributes['iso_datetime'])
                media_data = api.get_media(media[-1].id)
                end_time = datetime.fromisoformat(media_data.attributes['iso_datetime'])

            media_data = VideoData(iso_start_datetime=start_time,
                                   iso_end_datetime=end_time,
                                   platform=platform_type.name,
                                   camera=camera_type.name,
                                   mission=mission_name)
            info(f'Uploading {f}, start time {start_time}, end time {end_time}')
            create_video(tator_project.id, api, media_data, f.as_posix(), media_type.id, section)


@click.command("image", help="Load sequence of images into the database")
@common_args.host
@common_args.token
@common_args.project
@common_args.force
@click.option("--input", '-i', type=Path, help='path to the image directory')
@click.option("--input-left", '-l', type=Path, help='path to the left image directory')
@click.option("--input-right", '-r', type=Path, help='path to the right image directory')
@click.option("--log-depth", type=Path,
              help='path to the log with exported compass datetime/depth from the lcm logs')
@click.option("--log-position", type=Path,
              help='path to the log with exported USBL datetime/lat/lon from the lcm logs')
@click.option("--platform-type", type=Platform, default=Platform.MINI_ROV, required=True)
@click.option("--camera-type", type=Camera, default=Camera.FLIR, required=True)
@click.option("--mission-name", type=str, required=True)
@click.option("--max-images", required=False, type=int, help="Max number of images to load")
def load_image(input: Path, input_left: Path, input_right: Path, log_depth: Path, log_position: Path, host: str,
               token: str, project: str,
               platform_type: Platform, camera_type: Camera, mission_name: str, force: bool, max_images: int):
    """
    Load image(s) from a local file system to the database
    :param mission_name:
    :param camera_type:
    :param platform_type:
    :param input: Absolute path to the video to load
    :param log_position:
    :param log_depth:
    :param host: Hostname, e.g. localhost
    :param token: Authentication token
    :param project: Project name to load to
    :param force: True to force load and skip over check
    :param max_images: Maximum number of images to load
    :return:
    """
    image_path = input
    image_path_left = input_left
    image_path_right = input_right
    if image_path and not image_path.exists():
        err(f'Could not find {image_path}')
        return
    if input_left and not input_left.exists():
        err(f'Could not find {image_path_left}')
        return
    if input_right and not input_right.exists():
        err(f'Could not find {image_path_right}')
        return
    if not log_depth.exists():
        err(f'Could not find {log_depth}')
        return
    if not log_position.exists():
        err(f'Could not find {log_position}')
        return

    stereo = False
    if input_left and input_right:
        stereo = True

    api, tator_project = init_api_project(host, token, project)

    image_type = find_media_type(api, tator_project.id, "Image")
    ste_image_type = find_media_type(api, tator_project.id, "StereoImage")

    assert image_type is not None, f'Could not find type Image in project {tator_project.name}'
    assert ste_image_type is not None, f'Could not find type StereoImage in project {tator_project.name}'

    acceptable_extensions = ['.jpg', '.png', '.jpeg', 'tif']
    images_to_load = []
    if image_path_left:
        for ext in acceptable_extensions:
            new_images = sorted(image_path_left.rglob(f"*{ext}"))
            if len(new_images) > 0:
                images_to_load.extend(new_images)
                info(f'Found {len(new_images)} left images to load')

    if image_path_right:
        for ext in acceptable_extensions:
            new_images = sorted(image_path_right.rglob(f"*{ext}"))
            if len(new_images) > 0:
                images_to_load.extend(new_images)
                info(f'Found {len(new_images)} right images to load')

    if image_path:
        for ext in acceptable_extensions:
            new_images = sorted(image_path.rglob(f"*{ext}"))
            if len(new_images) > 0:
                images_to_load.extend(new_images)
                info(f'Found {len(new_images)} left images to load')

    if len(images_to_load) == 0:
        err(f'Could not find any images')
        return

    if max_images:
        info(f'Loading first {max_images} images')

    if force or click.confirm('Are you sure you want to load this?'
                              'You may want to check the database first to see if it is are already '
                              'loaded. Add --force to load anyway.'):

        # Search for the depth and lat/lon from the log files that is nearest to the image timestamp
        df = search_nearest(log_depth, log_position, images_to_load, max_images)
        if df is None:
            err(f'Could not find depth and lat/lon for the images in {log_depth} and {log_position}')
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            remap_left_files = []
            remap_right_files = []
            remap_files = []

            # Convert any images from .tif to png as tator does not support tif
            has_tiff = any([image.suffix == '.tif' for image in images_to_load])
            if has_tiff:
                for key, row in df.iterrows():
                    info(f'Converting {row}')
                    if stereo:
                        im_path = Path(row.left)
                        im_l = cv2.imread(row.left)
                        new_file = temp_path / f'{im_path.stem}_LEFT.png'
                        cv2.imwrite(new_file.as_posix(), im_l)
                        remap_left_files.append(new_file.as_posix())
                        im_r = cv2.imread(row.right)
                        im_path = Path(row.right)
                        new_file = temp_path / f'{im_path.stem}_RIGHT.png'
                        cv2.imwrite(new_file.as_posix(), im_r)
                        remap_right_files.append(new_file.as_posix())
                    else:
                        im_path = Path(row.image)
                        im = cv2.imread(row.image)
                        new_file = temp_path / f'{im_path.stem}.png'
                        cv2.imwrite(new_file.as_posix(), im)
                        remap_files.append(new_file.as_posix())

                # Replace the left and right and with names with the new temporary names for upload
                if stereo:
                    df['left'] = remap_left_files
                    df['right'] = remap_right_files

            i = 1
            section = f'{platform_type.name}/{camera_type.name}/{mission_name}'
            for index, row in df.iterrows():
                info(f'Uploading {row}')
                i += 1

                # if there is a left and right  column, then this is a stereo image
                # or, if the camera type is STEREOPI, then this is a stereo image
                # Add both left/right images to the database and create a stereo image on-the-fly
                if stereo or camera_type == Camera.STEREOPI:
                    ste_image_data = StereoImageData(
                        platform=platform_type.name,
                        camera=camera_type.name,
                        mission=mission_name,
                        iso_datetime=row.iso_datetime,
                        latitude=row.latitude,
                        longitude=row.longitude,
                        depth=row.depth
                    )

                    if camera_type == Camera.STEREOPI:
                        create_stereo_image(tator_project.id, api, ste_image_data, row.image, ste_image_type.id, section)
                    else:
                        # Combine the images into a single stereo image
                        im_left = cv2.imread(row.left)
                        im_right = cv2.imread(row.right)
                        im_stereo = np.hstack((im_left, im_right))

                        # Name the stereo image with the timestamp
                        ste_name = f'{row.iso_datetime.timestamp()}'
                        im_out = temp_path / f'{ste_name}.png'
                        cv2.imwrite(im_out.as_posix(), im_stereo)
                        create_stereo_image(tator_project.id, api, ste_image_data, im_out.as_posix(), ste_image_type.id,
                                            section)

                        # Add the left and right images to the database
                        image_data = ImageData(
                            platform=platform_type.name,
                            camera=camera_type.name,
                            mission=mission_name,
                            iso_datetime=row.iso_datetime,
                            latitude=row.latitude,
                            longitude=row.longitude,
                            depth=row.depth)
                        create_image(tator_project.id, api, image_data, row.left, image_type.id)
                        create_image(tator_project.id, api, image_data, row.right, image_type.id)

                else:
                    image_data = ImageData(
                        platform=platform_type.name,
                        camera=camera_type.name,
                        mission=mission_name,
                        iso_datetime=row.iso_datetime,
                        latitude=row.latitude,
                        longitude=row.longitude,
                        depth=row.depth)
                    create_image(tator_project.id, api, image_data, row.image, image_type.id, section)


def create_stereo_view_video(api: tator.api, tator_project: tator.models.Project, type_name: str,
                             left_media: tator.models.Media,
                             right_media: tator.models.Media):
    # Get the stereo image type
    media_types = api.get_media_type_list(tator_project.id)
    if len(media_types) == 0:
        err(f'Could not find types StereoImage')
        return

    # Get the type id
    multi_type = [t for t in media_types if t.name == type_name]

    # There should just be one type of this name
    if len(multi_type) != 1:
        err(f'Could not find type {type_name}')
        return

    multi_type = multi_type[0].id

    # Layout is rows, columns
    layout = [1, 2]

    # Copy the attributes from the left image
    attributes = left_media.attributes # type: dict

    # Combine the names of the two images to create a new name
    # Create a name using the left keeping everything to the left of _LEFT
    vid_out = f'{left_media.name.split('_LEFT')[0]}'
    section = type_name
    # Create attribute for multi-stream
    try:
        response = make_multi_stream(api, multi_type, layout, vid_out, [left_media.id, right_media.id], section)
        print(response)
        # Update the attributes with the left media attributes
        id = response.id
        api.update_media(id[0], {"attributes": {"platform": attributes['platform'],
                                    "camera": attributes['camera'],
                                    "mission": attributes['mission'],
                                    "iso_start_datetime": attributes['iso_start_datetime'],
                                    "iso_end_datetime": attributes['iso_end_datetime']}})

    except Exception as e:
        if 'list' not in str(e):  # Skip over 'list' object has no attribute 'items' error
            err(f'Error uploading {vid_out}: {e}')

    info(f'Uploaded {vid_out}')

@click.command("stereo-view", help="Load stereo view of two video files. Video files must be the same length and be loaded")
@common_args.host
@common_args.token
@common_args.project
@common_args.force
@click.option('--input-left', '-l', type=str, required=True, help='Name of the left video')
@click.option('--input-right', '-r', type=str, required=True, help='Name of the right video')
def create_stereo_view(host: str, token: str, project: str, input_left: str, input_right: str, force: bool):
    """
    Create stereo view of two video files
    :return:
    """

    api, tator_project = init_api_project(host, token, project)
    # Check that the media are in the database
    left_media = api.get_media_list(tator_project.id, name=input_left)
    right_media = api.get_media_list(tator_project.id, name=input_right)

    if len(left_media) == 0:
        err(f'Could not find media {input_left}')
        raise FileNotFoundError
    if len(right_media) == 0:
        err(f'Could not find media {input_right}')
        raise FileNotFoundError

    # Get the 'Video' type
    media_types = api.get_media_type_list(tator_project.id)
    if len(media_types) == 0:
        err(f'Could not find types Video')
        return
    video_type = [t for t in media_types if t.name == 'Video']
    video_type = video_type[0].id

    # Only works for video
    if left_media[0].type != video_type:
        err(f'Left media {input_left} is not a video')
        raise FileNotFoundError

    if right_media[0].type != video_type:
        err(f'Right media {input_right} is not a video')
        raise FileNotFoundError

    # Create the stereo view
    create_stereo_view_video(api, tator_project, 'StereoVideo', left_media[0], right_media[0])


@click.command("state", help="Load state associated with the video into the database")
@common_args.host
@common_args.token
@common_args.project
@common_args.force
@click.option("--video", '-v', help='path to the video')
@click.option("--log", '-v', help='path to the log with exported correct datetime/depth/lat/lon')
def load_state(video: str, log: str, host: str, token: str, project: str, force: bool):
    """
    Load video from a local file system to the database
    :param video: Absolute path to the video to load
    :param log: Absolute path to the log with corrected timestamp/depth/lat/lon for the video frames
    :param host: Hostname, e.g. localhost
    :param token: Authentication token
    :param project: Project name to load to
    :param force: True to force load and skip over check
    :return:
    """
    info('Not implemented yet')
    pass