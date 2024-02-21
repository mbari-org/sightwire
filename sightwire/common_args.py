# sightwire, Apache-2.0 license
# Filename: common_args.py
# Description: Common arguments for processing commands
import os

import click

# Common arguments for processing commands
host = click.option("--host", type=str, default=os.getenv('TATOR_HOST', 'http://localhost:8080'), required=False)
token = click.option("--token", type=str, default=os.environ['TATOR_TOKEN'], required=False)
project = click.option("--project", default=os.getenv('TATOR_PROJECT', '902204-CoMPAS'), required=False)
force = click.option("--force", is_flag=True, help='Force load and skip over check')
base_url = click.option( "--base-url", '-u', type=str, help='base url to the images, e.g. http://localhost:8000/compas/')
vol_map = click.option( "--vol-map", '-v', type=str, help="mapping from the path outside docker to internal docker, e.g. --vol-map '/home/ops/data:/data,/mnt/raid:/raid'")


def parse_vol_map(vol_map: str):
    _vol_map = {}
    if vol_map:
        for pair in vol_map.split('.'):
            key, value = pair.split(':')
            _vol_map[key] = value
    # Error if vol_map is not a dictionary if base_url is set
    if base_url and not _vol_map:
        raise(f'Need to add vol_map, e.g. --vol-map "/home/ops/data:/data,/mnt/raid:/raid" if base_url is set')

    return _vol_map