# sightwire, Apache-2.0 license
# Filename: convertors/commands.py
# Description:  Run data conversions for video, lcm logs, etc.
import logging

import click
from pathlib import Path
import pandas as pd

from sightwire.logger import info
from .lcm import parse_log, write_usbl_csv, write_depth_csv
from .video_transcoders import image_to_mp4


@click.command("create-video", help="Create mp4 video files from images")
@click.option('--input', '-i', type=Path, required=True, help='Path to the images')
@click.option('--num-images', type=int, default=30, required=False, help='(Optional) number of images to use in the mp4')
@click.option('--output', '-o', type=Path, required=True,  help='Path to the save the mp4 file')
@click.option('--csv', type=Path, required=True, help='Path to the save the csv file with timestamps')
def create_video(input: Path, num_images: int, output: Path, csv: Path):
    """
    Create mp4 files from images
    :return:
    """
    image_path = input
    mp4_path = output
    csv_path = csv

    # Some basic checks
    if not image_path.exists():
        info(f"Image path {image_path} does not exist")
        return

    mp4_path.parent.mkdir(parents=True, exist_ok=True)

    if 'bayer' in image_path.as_posix():
        info(f"Creating mp4 from bayer images {image_path}")
        data = image_to_mp4(image_path.as_posix(), mp4_path.as_posix(), demosaic=True, num_images=num_images)
        if data:
            info(f"Created {mp4_path} found {len(data)} images for {image_path}")
        else:
            info(f"Unable to create mp4 from bayer images {image_path}")
    else:
        info(f"Creating mp4 from images {image_path}")
        data = image_to_mp4(image_path.as_posix(), mp4_path.as_posix(), num_images=num_images)
        if data:
            info(f"Created {mp4_path} found {len(data)} images for {image_path}")
        else:
            info(f"Unable to create mp4 from images {image_path}")

    # Save the timestamp->filename mapping to a csv file
    df = pd.DataFrame(data, columns=['timestamp', 'filename'])
    df.to_csv(f'{csv_path.parent}/{mp4_path.stem}.csv', index=False)


@click.command("extract-log", help="Extract timestamp, depth, position, etc. from lcm logs")
@click.option("--log", type=Path,  required=True, help="LCM log file")
@click.option('--usbl-channel', '-i', required=True, help='USBL channel name (gps_fix_t)')
@click.option('--depth-channel', '-i', required=True, help='Depth channel name (depth_t)')
@click.option('--output', '-o', required=True, help='Filtered output file of raw combined USBL and depth events')
@click.option('--prefix', '-p', required=True, help='File prefix for output files')
def extract_log(log: Path, usbl_channel: str, depth_channel: str, output: str, prefix: str):
    """
    Extract navigation data (lat/lon, depth) from an LCM log using CoMPAS LCM types.
    """

    # Check if the LCM log file exists
    if not log.exists():
        logging.error(f"LCM log file {log} does not exist")

    info(f"Parsing LCM log {log}")

    # Parse the LCM log to extract USBL and depth data
    usbl_data, depth_data = parse_log(log, usbl_channel, depth_channel)

    info(f"Found {len(usbl_data)} USBL events")
    info(f"Found {len(depth_data)} depth events")

    # Write USBL data to a CSV file
    output_path = Path(output) / f"{prefix}_{usbl_channel}.csv"
    write_usbl_csv(output_path.as_posix(), usbl_data)
    info(f"Wrote USBL data to {output_path}")

    # Write depth data to a CSV file
    output_path = Path(output) / f"{prefix}_{depth_channel}.csv"
    write_depth_csv(output_path.as_posix(), depth_data)
    info(f"Wrote depth data to {output_path}")


if __name__ == "__main__":
    create_video()
