# sightwire, Apache-2.0 license
# Filename: convertors/video.py
# Description: Common video transcoding functions
from typing import List, Tuple

import cv2
import numpy as np
import shutil

from datetime import datetime
from tempfile import TemporaryDirectory as tempdir
from pathlib import Path

from moviepy.editor import ImageSequenceClip

from sightwire.logger import info
from sightwire.converters.time_utils import convert_timestamp_to_datetime_16, convert_timestamp_to_datetime_10


def image_to_mp4(image_path: str, output_mp4: str, demosaic: bool = False, num_images=None) -> List[Tuple[datetime, str]]:
    """
    Creates a movie from a collection of images in sorted order
    :param image_path: The path to the images
    :param output_mp4: The movie file to save the created movie to
    :param demosaic: (optional) Whether to demosaic the image
    :param num_images: (optional) Maximum number of images to use
    :return: Tuple with sorted timestamp in timestamp(datetime), filename  in order of the images stacked in the mp4
    """
    image_path = Path(image_path)
    images = sorted(image_path.glob("*.tif"))
    images += sorted(image_path.glob("*.png"))
    images += sorted(image_path.glob("*.jpg"))
    images += sorted(image_path.glob("*.jpeg"))
    timestamps = []

    acceptable_suffixes = ['.jpg', '.jpeg', '.png']

    # if there are no images, or not at least two then return
    if len(images) == 0 or len(images) == 1:
        assert False, f"Not enough images found in {image_path}"
        return []

    # Working in a temporary directory, convert the images to  .jpg files
    with tempdir() as workdir:
        image_sequence = []
        work_path = Path(workdir)
        suffix = 'jpg'
        for cnt, i in enumerate(images):
            # Get the timestamp from the filename
            if len(i.stem) == 16:
                timestamps.append(convert_timestamp_to_datetime_16(i.stem))
            elif len(i.stem) == 10:
                timestamps.append(convert_timestamp_to_datetime_10(i.stem))
            else:
                timestamps.append(convert_timestamp_to_datetime_10(i.stem))

            # if this is a JPG or PNG file, then we can just copy it over
            if i.suffix.lower() in acceptable_suffixes and not demosaic:
                image_out = work_path / f'{i.stem}.{i.suffix}'
                shutil.copy(i.as_posix(), image_out.as_posix())
                suffix = i.suffix
            else:
                image_out = work_path / f'{i.stem}.jpg'

                raw_img = cv2.imread(i.as_posix(), cv2.IMREAD_UNCHANGED)
                cv2.imwrite(image_out.as_posix(), raw_img)

            image_sequence.append(image_out.as_posix())
            if cnt % 100 == 0:
                info(f"Preparing {cnt} images for {output_mp4}...")
            if num_images and cnt > num_images > 0:
                info(f"Stopping at {num_images} images")
                break

        # Create the video from the .jpg files - doesn't work with .tif files
        l = sorted(work_path.glob(f'*.{suffix}'))
        l = [i.as_posix() for i in l]

        # Calculate the time stamp and infer the frame rate from the first two images
        if len(images[0].stem) == 16:
            timestamps = [(convert_timestamp_to_datetime_16(i.stem), i.as_posix()) for i in images]
        elif len(images[0].stem) == 10:
            timestamps = [(convert_timestamp_to_datetime_10(i.stem), i.as_posix()) for i in images]
        t0 = timestamps[0][0]
        t1 = timestamps[1][0]
        fps = np.ceil(1/(t1 - t0).total_seconds())

        assert fps > 0, "fps must be greater than 0"

        # Create the video
        info(f"Creating {output_mp4} from {len(timestamps)} images at {fps} fps...")
        image_sequence = ImageSequenceClip(l, fps=fps, with_mask=False)
        image_sequence.write_videofile(output_mp4)

        return timestamps
