# sightwire, Apache-2.0 license
# Filename: loaders/capture_load_livestream.py
# Description: Captures images from a live stream and uploads them to Tator. Similar to the image loader, but for live streams to simulate a LCM image capture.
import time
from pathlib import Path

import cv2
import sys
import click

from sightwire import common_args
from sightwire.database.common import init_api_project, find_media_type
from sightwire.logger import info, err


@click.command("capture", help="Captures images from a live stream to a directory. Run scripts/create_livestream.sh to start a live stream first.")
@common_args.host
@common_args.token
@common_args.project
@click.option("--stream", '-u', type=str, help='e.g. rtmp://atuncita:1935/streaml')
@click.option("--output", '-o', type=Path, help='path to the image directory to save the images. Must be a directory and mounted in the nginx container')
@click.option("--max-images", required=False, type=int, help="Max number of images to load. Useful for testing. Exits after loading this many images.")
@click.option("--stride", required=False, default=50, type=int, help="stride to skip frames")
def capture_livestream(stream: str, output:Path, host: str, token: str, project: str, stride:int, max_images: int):

    output.mkdir(parents=True, exist_ok=True)

    api, project = init_api_project(host, token, project)
    image_type = find_media_type(api, project.id, "Image")
    assert image_type is not None, f'Could not find type Image in project {project.name}'

    cap = cv2.VideoCapture(stream)
    if (cap.isOpened() == False):
        print(f'Unable to open URL {stream} !!!')
        sys.exit(-1)
    
    # retrieve FPS and calculate how long to wait between each frame to be display
    fps = cap.get(cv2.CAP_PROP_FPS)
    info(f'FPS:{fps}')
    
    # calculate wait time
    wait_ms = int(1000 / fps)
    info(f'Wait time: {wait_ms} ms')

    i = 0
    num_captured = 0

    while (True):
        # read one frame
        ret, frame = cap.read()

        if ret == False:
            err(f'Error reading frame {i} from URL {stream} !!!')
            break

        # Only capture every 50th frame with is about 10 seconds
        if i % stride == 0:
            # Resize Mat by 25%
            # frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            current_time_seconds = int(time.time())
            microseconds = int((time.time() - current_time_seconds) * 1000000)

            # Format the filename based on a string of the seconds + 6 digits of the microsecond
            file_loc = output / f'{current_time_seconds}{microseconds:06d}.png'
            cv2.imwrite(file_loc.as_posix(), frame)
            num_captured += 1

        # display frame
        cv2.imshow(f'{output}', frame)
        i += 1
        if cv2.waitKey(wait_ms) & 0xFF == ord('q') or max_images is not None and num_captured >= max_images: # press q to quit
            break

    cap.release()
    cv2.destroyAllWindows()
    info('Capture complete')
