# sightwire, Apache-2.0 license
# Filename: common_args.py
# Description: Common arguments for processing commands
import os

import click

# Common arguments for processing commands
host = click.option("--host", type=str, default=os.getenv('TATOR_HOST', 'localhost'), required=False)
token = click.option("--token", type=str, default=os.environ['TATOR_TOKEN'], required=False)
project = click.option("--project", default=os.getenv('TATOR_PROJECT', '902204-CoMPAS'), required=False)
force = click.option("--force", required=False, type=bool, default=False, help='Force load and skip over check')