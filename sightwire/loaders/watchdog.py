# sightwire, Apache-2.0 license
# Filename: loaders/watchdog.py
# Description: Watchdog based loading for near real-time capture.
# Enqueue jobs on a Redis TimeSeries queue when files are created in a directory
import os
from dataclasses import asdict
import time
from pathlib import Path

import click
import pandas as pd
import redis

from common_args import parse_vol_map
from sightwire import common_args
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sightwire.converters.time_utils import convert_timestamp_to_datetime_16
from sightwire.database.common import init_api_project, find_media_type, find_state_type
from sightwire.database.data_types import Platform, Camera, Side, StereoImageData
from sightwire.loaders.image_utils import create_media
from sightwire.logger import info, debug, err

count = 0


@click.command("load", help="Consume REDIS timeseries messages and load")
@common_args.host
@common_args.token
@common_args.project
@common_args.base_url
@common_args.vol_map
@click.option("--platform-type", type=Platform, default=Platform.MINI_ROV, required=True)
@click.option("--camera-type", type=Camera, default=Camera.FLIR, required=True)
@click.option("--mission-name", type=str, required=True)
@click.option("--input", '-l', type=Path, help='base path to the directory to watch')
def load_watchdog(base_url: str, vol_map: str, host: str, token: str, project: str, input: Path,
                  platform_type: Platform, camera_type: Camera, mission_name: str):
    info(f'Consuming Redis TimeSeries queue for project {project} on host {host}')

    _vol_map = parse_vol_map(vol_map)

    # Initialize the Tator API
    api, project = init_api_project(host, token, project)

    # Create a Redis connection
    r = redis.Redis(port=6380)

    # Create a Redis TimeSeries queue
    ts = r.ts()

    # Create a Redis TimeSeries queue
    queue_name_l = None
    queue_name_r = None
    for subdir in input.iterdir():
        if subdir.is_dir():
            if "_L_" in subdir.name:
                queue_name_l = subdir.as_posix()
            elif "_R_" in subdir.name:
                queue_name_r = subdir.as_posix()
    assert queue_name_l is not None, f'Could not find a LEFT directory in {input}'
    assert queue_name_r is not None, f'Could not find a RIGHT directory in {input}'

    # Get the image type and stereo state type
    image_type = find_media_type(api, project.id, "Image")
    ste_state_type = find_state_type(api, project.id, "Stereo")

    section = f'REALTIME{platform_type.name}/{camera_type.name}/{mission_name}'

    def parse_dict(data):
        directory, meta_data = list(data.items())[0]
        filename = f"{meta_data[1]}.png"
        return f"{directory}/{filename}"

    def load_pair(path_left, path_right, timestamp_left: int, timestamp_right: int):
        """
        Load an image pair into the database
        """

        # Convert the timestamp to a datetime
        iso_datetime_left = convert_timestamp_to_datetime_16(timestamp_left)
        iso_datetime_right = convert_timestamp_to_datetime_16(timestamp_right)

        row_l = pd.Series(
            {'left': parse_dict(path_left[0]), 'iso_datetime': iso_datetime_left, 'latitude': 0, 'longitude': 0, 'depth': 0})
        row_r = pd.Series(
            {'right': parse_dict(path_right[0]), 'iso_datetime': iso_datetime_right, 'latitude': 0, 'longitude': 0, 'depth': 0})

        # Create a media for the left/right
        left_id = create_media(project.id, api, row_l, base_url, _vol_map, image_type.id, section, Side.LEFT,
                               platform_type, camera_type, mission_name)
        right_id = create_media(project.id, api, row_r, base_url, _vol_map, image_type.id, section, Side.RIGHT,
                                platform_type, camera_type, mission_name)

        # Create a state to link the left and right
        # # Add the left and right images to a stereo state using the left media timestamp
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
    while True:  # Loop forever
        try:
            left_job = ts.mget(["side=L"], with_labels=True)
            if len(left_job) > 0 and len(left_job[0]) > 0:
                debug(left_job)
                debug(f"left_job timestamp: {left_job[0][queue_name_l][1]}")

            right_job = ts.mget(["side=R"], with_labels=True)
            if len(right_job) > 0 and len(right_job[0]) > 0:
                debug(right_job)
                debug(f"right_job timestamp: {right_job[0][queue_name_r][1]}")

            # If both the right and left jobs exist
            if len(right_job) > 0 and len(right_job[0]) > 0 and left_job[0] and len(left_job[0]) > 0:
                # Check if the time difference between the right and left is less than 500 milliseconds
                right_timestamp = right_job[0][queue_name_r][1]
                left_timestamp = left_job[0][queue_name_l][1]
                time_diff = abs(right_timestamp - left_timestamp) / 1e6
                debug(f'Time difference: {time_diff}')
                if time_diff < 500:
                    debug(f'Loading pair: {right_job} and {left_job}')
                    load_pair(left_job, right_job, left_timestamp, right_timestamp)
        except Exception as ex:
            err(ex)

        # TODO: account for the load time in sleep
        time.sleep(1)
        debug('Waiting 1 second for next available image pair')


@click.command("run_watchdog",
               help="A watcher that monitors a directory for new images and puts them into a Redis TimeSeries queue")
@click.option("--input", '-l', type=Path, help='base path to the directory to watch')
def run_watchdog(input: Path):
    """
    This is a watcher that monitors a directory for new images and puts them into a Redis TimeSeries queue
    """

    # Create a Redis connection and test it
    r = redis.Redis(port=6380, decode_responses=True)
    r.ping()

    # Create a Redis TimeSeries queue
    queue_name_l = None
    queue_name_r = None
    for subdir in input.iterdir():
        if subdir.is_dir():
            if "_L_" in subdir.name:
                queue_name_l = subdir.as_posix()
            elif "_R_" in subdir.name:
                queue_name_r = subdir.as_posix()

    assert queue_name_l is not None, f'Could not find a LEFT directory in {input}'
    assert queue_name_r is not None, f'Could not find a RIGHT directory in {input}'
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
                   duplicate_policy="LAST",
                   timestamp=timestamp_int,
                   value=count,
                   labels={"side": "L"})
        if '_R_' in path:
            info(f'Enqueueing job for {path} at {timestamp}')
            ts.add(queue_name_r,
                   duplicate_policy="LAST",
                   timestamp=timestamp_int,
                   value=count,
                   labels={"side": "R"})
        count += 1

    def wait_for_file_size(file_path: str):
        """
         Simple check to wait for file system to stop changing up to 10 attempts
        """
        retries = 0
        initial_size = -1
        while retries < 10:
            current_size = os.path.getsize(file_path)
            if current_size == initial_size:
                return True
            initial_size = current_size
            retries += 1
        return False

    class PngHandler(FileSystemEventHandler):
        """
        File system event handler that enqueues jobs on the Redis TimeSeries queue
        Listens for files created with a .png extension
        """

        def on_created(self, event):
            debug(f'{event.src_path} created')
            if event.src_path.endswith('.png'):
                if wait_for_file_size(event.src_path):
                    enqueue_job(event.src_path, event)
                else:
                    err(f'File size not stablized for {event.src_path}')

    observer = Observer()

    # Schedule the file system event handler. Add the recursive=True argument to listen for events in subdirectories
    # as it is assumed RIGHT/LEFT images are in separate directories
    observer.schedule(PngHandler(), path=input.as_posix(), recursive=True)

    # Start the observers
    observer.start()

    # Wait for the observers to finish
    observer.join()
