# sightwire, Apache-2.0 license
# Filename: __main__
# Description: Main entry point for the sightwire command line interface
from datetime import datetime
from pathlib import Path

import click

from sightwire.loaders import commands as loaders
from sightwire.converters import commands as converters
from sightwire.database import commands as database
from sightwire.logger import info, err, create_logger_file
from sightwire import __version__


create_logger_file(log_path=Path.home() / 'sightwire' / 'logs')

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(
    __version__,
    '-V', '--version',
    message=f'%(prog)s, version %(version)s'
)
def cli():
    """
    Run CoMPAS data workflows
    """
    pass


@cli.group(name="database")
def cli_database():
    """
    Commands related to database management
    """
    pass


cli.add_command(cli_database)
cli_database.add_command(database.init)


@cli.group(name="convert")
def cli_convert():
    """
    Commands related to converting data
    """
    pass


cli.add_command(cli_convert)
cli_convert.add_command(converters.create_video)
cli_convert.add_command(converters.extract_log)


@click.group(name="load")
def cli_load():
    """
    Commands related to loading data
    """
    pass


cli.add_command(cli_load)
cli_load.add_command(loaders.load_image)
cli_load.add_command(loaders.load_video)
cli_load.add_command(loaders.create_stereo_view)

if __name__ == '__main__':
    try:
        start = datetime.utcnow()
        cli()
        end = datetime.utcnow()
        info(f'Done. Elapsed time: {end - start} seconds')
    except Exception as e:
        err(f'Exiting. Error: {e}')
        exit(-1)
