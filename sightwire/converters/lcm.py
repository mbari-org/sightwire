# sightwire, Apache-2.0 license
# Filename: convertors/lcm.py
# Description:  LCM logs conversion courtesy K. Barnard. Replaced argparse with click and restyled.
from datetime import timedelta
from pathlib import Path
from typing import List, Tuple
 
from sightwire.logger import info
from lcmlog import LogReader, LogWriter, Event
from compas_lcmtypes.senlcm import gps_fix_t, depth_t
 

def parse_log(log_path: Path, usbl_channel: str, depth_channel: str) -> Tuple[List[Event], List[Event]]:
    """
    Parse an LCM log and extract navigation data.
    :param log_path: Path to the LCM log file.
    :param usbl_channel (str) USBL channel name.
    :param depth_channel (str) Depth channel name.
    :returns:
        Tuple[List[Event], List[Event]]: A tuple containing two lists:
            - usbl_data: List of USBL events.
            - depth_data: List of depth events.
    """
    # Initialize empty lists to store the extracted data
    usbl_data = []
    depth_data = []

    # Create a LogReader object to read the LCM log file
    reader = LogReader(str(log_path))

    # Iterate over each event in the LCM log
    first_timestamp = None
    for idx, event in enumerate(reader, start=1):
        # Calculate the time difference from the first event
        timestamp = event.header.timestamp
        if first_timestamp is None:
            first_timestamp = timestamp
        microsecond_delta = timestamp - first_timestamp
        td = timedelta(microseconds=microsecond_delta)

        # Log the progress every 10000 events
        if idx % 10000 == 0:
            info(f"Processing event {idx} at {td}")

        # Collect USBL and depth events
        if event.channel == usbl_channel:
            usbl_data.append(event)
        elif event.channel == depth_channel:
            depth_data.append(event)

    # Return the extracted USBL and depth data
    return usbl_data, depth_data


def write_log(log_path: Path, data: List[Event]):
    """
    Write an LCM log file. Events will be sorted by timestamp
    :log_path Path to LCM log file
    :data List of events
    """
    writer = LogWriter(str(log_path))
    for event in sorted(data, key=lambda e: e.header.timestamp):  # Sort by event timestamp
        writer.write(event)


def write_usbl_csv(output_path: Path, usbl_data: List[Event]):
    """
    Write USBL data to a CSV file
    :output_path: Path to output file
    :usbl_data: List of USBL events
    """
    with open(output_path, "w") as f:
        f.write("lcm_timestamp,sensor_timestamp,latitude,longitude,altitude\n")
        for event in usbl_data:
            message = gps_fix_t.decode(event.data)
            f.write(
                f"{event.header.timestamp},{message.header.timestamp},{message.latitude},{message.longitud},{message.altitude}\n"
            )


def write_depth_csv(output_path: Path, depth_data: List[Event]):
    """
    Write depth data to a CSV file
    :output_path: Path to output file
    :depth_data: List of depth events
    """
    with open(output_path, "w") as f:
        f.write("lcm_timestamp,sensor_timestamp,depth,pressure\n")
        for event in depth_data:
            message = depth_t.decode(event.data)
            f.write(f"{event.header.timestamp},{message.header.timestamp},{message.depth},{message.pressure}\n")
