# sightwire, Apache-2.0 license
# Filename: loaders/watchdog.py
# Description: Enqueue jobs on a Redis TimeSeries queue when files are created in a directory
from dataclasses import asdict
from datetime import datetime, time
from pathlib import Path

import click
import pandas as pd
import redis
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sightwire.converters.time_utils import convert_timestamp_to_datetime_16
from sightwire.database.common import init_api_project, find_media_type, find_state_type
from sightwire.database.data_types import Platform, Camera, Side, StereoImageData
from sightwire.loaders.image_utils import create_media
from sightwire.logger import info, debug


@click.option("--base-url", '-u', type=str, help='base url to the images, e.g. http://localhost:8000/compas/')
@click.option("--platform-type", type=Platform, default=Platform.MINI_ROV, required=True)
@click.option("--camera-type", type=Camera, default=Camera.FLIR, required=True)
@click.option("--mission-name", type=str, required=True)
def consume_ts(base_url:str, host: str, token: str, project: str,
               platform_type: Platform, camera_type: Camera, mission_name: str):

    info(f'Consuming Redis TimeSeries queue for project {project} on host {host}')

    # Create a Redis connection
    r = redis.Redis(port=6380)

    # Create a Redis TimeSeries queue
    ts = r.ts()

    # Initialize the Tator API
    api, project = init_api_project(host, token, project)

    # Get the image type and stereo state type
    image_type = find_media_type(api, project.id, "Image")
    ste_state_type = find_state_type(api, project.id, "Stereo")

    section = f'LIVE{platform_type.name}/{camera_type.name}/{mission_name}'

    def load_pair(path_left, path_right, timestamp_left:int, timestamp_right:int):
        """
        Load an image pair into the database
        """

        # Convert the timestamp to a datetime
        iso_datetime_left = datetime.fromtimestamp(timestamp_left)
        iso_datetime_right = datetime.fromtimestamp(timestamp_right)

        row_l = pd.Series({'left': path_left, 'iso_datetime': iso_datetime_left, 'latitude': 0, 'longitude': 0, 'depth': 0})
        row_r = pd.Series({'right': path_right, 'iso_datetime': iso_datetime_right, 'latitude': 0, 'longitude': 0, 'depth': 0})

        # Create a media for the left/right
        left_id = create_media(project.id, api, row_l, base_url, image_type.id, section, Side.LEFT,
                                 platform_type, camera_type, mission_name)
        right_id = create_media(project.id, api, row_r, base_url, image_type.id, section, Side.RIGHT,
                                platform_type, camera_type, mission_name)

        # Create a state to link the left and right
        # Add the left and right images to a stereo state using the left media timestamp
        response = api.create_state_list(
            project=project.id,
            body={
                "type": ste_state_type.id,
                "media_ids": [left_id, right_id],
                "frame": 0,
                "attributes": asdict(StereoImageData(
                    platform=platform_type.value,
                    camera=camera_type.value,
                    mission=mission_name,
                    iso_datetime=row_l.iso_datetime))
            })
        info(f'Created stereo state {response.id} for media LEFT {left_id} and RIGHT {right_id}')

    # Loop through the jobs in the Redis TimeSeries queue every 1 second
    while True: # Loop forever
        left_job = ts.mget(["side=L"], with_labels=True)
        if len(left_job) > 0:
            debug(f"left_job timestamp: {left_job[0]['TS_PROSILICA_L'][1]}")

        right_job = ts.mget(["side=R"], with_labels=True)
        if len(right_job) > 0:
            debug(f"right_job timestamp: {right_job[0]['TS_PROSILICA_R'][1]}")

        # If both the right and left jobs exist
        if len(right_job) > 0 and len(left_job) > 0:
            # Check if the time difference between the right and left is less than 500 milliseconds
            right_timestamp = right_job[0]['TS_PROSILICA_R'][1]
            left_timestamp = left_job[0]['TS_PROSILICA_L'][1]
            time_diff = abs(right_timestamp - left_timestamp) / 1e6
            info(f'Time difference: {time_diff}')
            if time_diff < 500:
                debug(f'Loading pair: {right_job} and {left_job}')
                load_pair(right_job, left_job, left_timestamp, right_timestamp)

        time.sleep(1)

@click.command("watchdog", help="A watcher that monitors a directory for new images and puts them into a Redis TimeSeries queue")
@click.option("--input", '-l', type=Path, help='base path to the directory to watch')
def run_watchdog(input: Path):
    """
    This is a watcher that monitors a directory for new images and puts them into a Redis TimeSeries queue
    """

    # Create a Redis connection and test it
    r = redis.Redis(port=6380, decode_responses=True)
    r.ping()

    # Create a Redis TimeSeries queue
    queue_name_l = "TS_PROSILICA_L"
    queue_name_r = "TS_PROSILICA_R"
    ts = r.ts()

    # Create the queue if it does not exist
    for queue_name in [queue_name_l, queue_name_r]:
        if not r.exists(queue_name):
            ts.create(queue_name)
        # Purge the queue and set the retention period to 20 seconds
        ts.delete(queue_name, "-", "+")
        ts.alter(queue_name, retention_msecs=20000)
        if '_L' in queue_name:
            ts.alter(queue_name, labels={"side": "L"})
        if '_R' in queue_name:
            ts.alter(queue_name, labels={"side": "R"})


    count = 0
    def enqueue_job(path, event):
        """
        Enqueue a job on the Redis TimeSeries queue
        """
        global count
        # Get the timestamp of the event from the file, e.g. 1708033240797775.png is 1708033240797775
        timestamp_int = int(Path(event.src_path).stem)
        timestamp = convert_timestamp_to_datetime_16(int(Path(event.src_path).stem))
        if '_L_' in path:
            info(f'Enqueueing job for {path} at {timestamp}')
            # Enqueue the job on the left side of the queue
            ts.add(queue_name_l,
                   timestamp=timestamp_int,
                   value=count)
        if '_R_' in path:
            print(f'Enqueueing job for {path} at {timestamp}')
            ts.add(queue_name_r,
                   timestamp=timestamp_int,
                   value=count)
        count += 1


    class PngHandler(FileSystemEventHandler):
        """
        File system event handler that enqueues jobs on the Redis TimeSeries queue
        Listens for files created with a .png extension
        """
        def on_created(self, event):
            if event.src_path.endswith('.png'):
                enqueue_job(event.src_path, event)


    observer = Observer()

    # Schedule the file system event handler. Add the recursive=True argument to listen for events in subdirectories
    observer.schedule(PngHandler(), path=input.as_posix(), recursive=True)

    # Start the observers
    observer.start()

    # Wait for the observers to finish
    observer.join()
