# sightwire, Apache-2.0 license
# Filename: loaders/load_video.py
# Description: Load video into the database

from datetime import datetime
from pathlib import Path

import click
from tator.util import make_multi_stream

from sightwire import common_args
from sightwire.converters.commands import create_video
from sightwire.database.common import init_api_project, find_media_type
from sightwire.database.data_types import Platform, Camera, VideoData
from sightwire.logger import info, err


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


@click.command("stereo-view",
               help="Load stereo view of two video files. Video files must be the same length and be loaded")
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

    left_media = left_media[0]
    right_media = right_media[0]

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

        # Get the stereo image type
    media_types = api.get_media_type_list(tator_project.id)
    if len(media_types) == 0:
        err(f'Could not find types StereoImage')
        return

    # Get the type id
    type_name = 'StereoVideo'
    multi_type = [t for t in media_types if t.name == type_name]

    # There should just be one type of this name
    if len(multi_type) != 1:
        err(f'Could not find type {type_name}')
        return

    multi_type = multi_type[0].id

    # Layout is rows, columns
    layout = [1, 2]

    # Copy the attributes from the left image
    attributes = left_media.attributes  # type: dict

    # Combine the names of the two images to create a new name
    # Create a name using the left keeping everything to the left of _LEFT
    vid_out = f"{left_media.name.split('_LEFT')[0]}"
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
