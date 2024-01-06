# sightwire, Apache-2.0 license
# Filename: database/localization.py
# Description:  Database operation related to localizations on images

import logging
from tator.openapi.tator_openapi import TatorApi
from sightwire.logger import info


def create_types(tator_api: TatorApi, project: int) -> None:
    """
    Create the localization types in the project. Only needs to be done once and fails if the types already exist.
    :param tator_api: :class:`TatorApi` object
    :param project: Project ID
    """

    loc_types = tator_api.get_localization_type_list(project=project)
    info(f"Found {len(loc_types)} existing localization types")
    assert len(loc_types) == 0

    media_types = tator_api.get_media_type_list(project=project)
    media_type_ids = [media_type.id for media_type in media_types]

    # Create the localization-associated state type
    spec = {
        "name": "Box",
        "description": "Localization associated type from object detection models",
        "dtype": "box",
        "visible": True,
        "grouping_default": True,
        "media_types": media_type_ids
    }

    response = tator_api.create_localization_type(project=project, localization_type_spec=spec)
    logging.info(response)
    info(response)