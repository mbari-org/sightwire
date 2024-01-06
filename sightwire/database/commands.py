# sightwire, Apache-2.0 license
# Filename: database/commands.py
# Description:  Database commands

from pathlib import Path

import click
import tator
import os
import sightwire.database.localization as compas_localization
import sightwire.database.media as compas_media
import sightwire.database.state as compas_state
from sightwire.logger import info
from sightwire.database.common import init_api_project


@click.command("init", help="Initialize the database")
def init():
    host = os.getenv('TATOR_HOST', 'localhost')
    token = os.environ['TATOR_TOKEN']
    project = os.getenv('TATOR_PROJECT', '902204-CoMPAS') # Default to CoMPAS project

    if click.confirm(f'WARNING: This will delete all existing media and localizations in the project {project} if '
                     f'they exist. Continue ?'):

        api, project = init_api_project(host, token, project)
        assert project is not None
        info(f"Found project {project.name} with id {project.id}")

        media_types = api.get_media_type_list(project=project.id)
        info(f"Found {len(media_types)} existing media")

        ###################### MEDIA TYPES
        # Remove existing media types
        info(f"Deleting {len(media_types)} existing state types")
        if len(media_types) > 0:
            for media_type in media_types:
                api.delete_media_type(media_type.id)

        # Create media types
        compas_media.create_types(tator_api=api, project=project.id)

        # ###################### LOCALIZATION TYPES
        localization_types = api.get_localization_type_list(project=project.id)
        info(f"Found {len(localization_types)} existing localization type")

        # Remove existing localization types
        info(f"Deleting {len(localization_types)} existing localization types")
        if len(localization_types) > 0:
            for localization_type in localization_types:
                api.delete_localization_type(localization_type.id)

        # Create localization types
        compas_localization.create_types(tator_api=api, project=project.id)

        # ###################### STATE TYPES
        # Remove existing state types
        state_types = api.get_state_type_list(project=project.id)
        info(f"Deleting {len(state_types)} existing state types")
        if len(state_types) > 0:
            for state_type in state_types:
                api.delete_state_type(state_type.id)

        # Create state types
        compas_state.create_types(tator_api=api, project=project.id)
