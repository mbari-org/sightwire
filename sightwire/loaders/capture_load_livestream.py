# sightwire, Apache-2.0 license
# Filename: loaders/capture_load_livestream.py
# Description: Captures images from a live stream and uploads them to Tator. Similar to the image loader, but for live streams to simulate a LCM image capture.
import tempfile
from datetime import datetime
from pathlib import Path

import cv2
import sys
import click
import pandas as pd

import common_args
from database.common import init_api_project, find_media_type, find_state_type
from database.data_types import Platform, Camera, Side
from loaders.image_utils import create_media
from logger import info


@click.command("livestream", help="Load images captured from a live stream into the database. Run scripts/create_livestream.sh to start a live stream first.")
@common_args.host
@common_args.token
@common_args.project
@click.option("--stream", '-u', type=str, help='e.g. rtmp://atuncita:1935/streaml')
@click.option("--output", '-o', type=Path, help='path to the image directory to save the images. Must be a directory and mounted in the nginx container')
@click.option("--base-url", '-u', type=str, help='base url to the images, e.g. http://localhost:8000/compas/')
@click.option("--platform-type", type=Platform, default=Platform.MINI_ROV, required=True)
@click.option("--camera-type", type=Camera, default=Camera.FLIR, required=True)
@click.option("--mission-name", type=str, required=True)
@click.option("--max-images", required=False, type=int, help="Max number of images to load. Useful for testing. Exits after loading this many images.")
def capture_livestream(stream_url: str,  output:Path, base_url:str, host: str, token: str, project: str,
               platform_type: Platform, camera_type: Camera, mission_name: str, max_images: int):

    output.mkdir(parents=True, exist_ok=True)

    api, project = init_api_project(host, token, project)
    image_type = find_media_type(api, project.id, "Image")
    assert image_type is not None, f'Could not find type Image in project {project.name}'

    # ste_state_type = find_state_type(api, project.id, "Stereo")
    # assert ste_state_type is not None, f'Could not find type Stereo in project {project.name}'

    section = f'LIVE{platform_type.name}/{camera_type.name}/{mission_name}'

    cap = cv2.VideoCapture(stream_url)
    if (cap.isOpened() == False):
        print(f'Unable to open URL {stream_url} !!!')
        sys.exit(-1)
    
    # retrieve FPS and calculate how long to wait between each frame to be display
    fps = cap.get(cv2.CAP_PROP_FPS)
    info('FPS:', fps)
    
    # calculate wait time
    wait_ms = int(1000 / fps)
    info('Wait time:', wait_ms)

    i = 0
    num_captured = 0
    while (True):
        # read one frame
        ret, frame = cap.read()

        # Only capture every 5th frame
        if i % 5 == 0:
            # Resize Mat by 25%
            # frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            file_loc = f'{output}/frame_{i}.png'
            cv2.imwrite(file_loc.as_posix(), frame)

            # Create a media for the left
            row = pd.Series({'left': file_loc, 'iso_datetime': datetime.now(), 'latitude': 0, 'longitude': 0, 'depth': 0})

            left_id = create_media(project.id, api, row, base_url, image_type.id, section, Side.LEFT,
                                   platform_type, camera_type, mission_name)

            num_captured += 1

            # Create a media for the right
            # row = pd.Series({'file_loc': file_loc, 'frame': i})
            # right_id = create_media(project.id, api, row, base_url, image_type.id, section, Side.RIGHT,
            #                         platform_type, camera_type, mission_name)

            # Create a state to link the left and right
            # Add the left and right images to a stereo state
            # response = api.create_state_list(
            #     project=project.id,
            #     body={
            #         "type": ste_state_type.id,
            #         "media_ids": [left_id, right_id],
            #         "frame": 0,
            #         "attributes": asdict(StereoImageData(
            #             platform=platform_type.value,
            #             camera=camera_type.value,
            #             mission=mission_name,
            #             iso_datetime=row.iso_datetime))
            #     })
            # info(f'Created stereo state {response.id} for media LEFT {left_id} and RIGHT {right_id}')

        # display frame
        cv2.imshow('frame', frame)
        i += 1
        if cv2.waitKey(wait_ms) & 0xFF == ord('q') or max_images is not None and num_captured >= max_images: # press q to quit
            break

    cap.release()
    cv2.destroyAllWindows()
