# sightwire, Apache-2.0 license
# Filename: loaders/load_localizations.py
# Description: Load localizations into the database

import click

import common_args
from logger import info


@click.command("box", help="Load localization box associated with an image into the database")
@common_args.host
@common_args.token
@common_args.project
@common_args.force
@click.option("--video", '-v', help='path to the video')
@click.option("--log", '-v', help='path to the log with exported correct datetime/depth/lat/lon')
def load_box(video: str, log: str, host: str, token: str, project: str, force: bool):
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
