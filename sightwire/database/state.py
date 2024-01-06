import logging

from tator.openapi.tator_openapi import TatorApi

from sightwire.logger import info


def create_types(tator_api: TatorApi, project: int) -> None:
    """
    Create the state types in the project. Only needs to be done once and fails if the state types already exist.
    :param tator_api: :class:`TatorApi` object
    :param project: Project ID
    """

    state_types = tator_api.get_state_type_list(project=project)
    info(f"Found {len(state_types)} existing state types")
    assert len(state_types) == 0

    media_types = tator_api.get_media_type_list(project=project)
    media_type_ids = [media_type.id for media_type in media_types]
    info(f"Found {len(media_type_ids)} media types")

    spec = {
        "name": "Experiment",
        "description": "Media associated state type for experiments at the frame level",
        "dtype": "state",
        "association": "Frame",
        "visible": True,
        "grouping_default": False,
        "media_types": media_type_ids,
        "attribute_types": [
            {
                "name": "iso_datetime",
                "dtype": "datetime",
            },
            {
                "name": "timestamp",
                "dtype": "int",
            },
            {
                "name": "depth",
                "dtype": "int",
            },
            {
                "name": "position",
                "dtype": "geopos",
                "default": [36.75276, -122.056],
            }
        ]
    }

    response = tator_api.create_state_type(project=project, state_type_spec=spec)
    logging.info(response)

    # Create the localization-associated state type
    spec = {
        "name": "Box",
        "description": "Localization associated state type from object detection models",
        "dtype": "state",
        "association": "Localization",
        "visible": True,
        "grouping_default": True,
        "media_types": media_type_ids,
        "attribute_types": [
            {
                "name": "prediction",
                "dtype": "string",
            },
            {
                "name": "score",
                "dtype": "int",
            },
        ]
    }

    response = tator_api.create_state_type(project=project, state_type_spec=spec)
    info(response)

    spec = {
        "name": "Saliency Localization",
        "description": "Localization associated state type from saliency models",
        "dtype": "state",
        "association": "Localization",
        "visible": True,
        "grouping_default": False,
        "media_types": media_type_ids,
        "attribute_types": [
            {
                "name": "score",
                "dtype": "int",
            },
        ]
    }

    response = tator_api.create_state_type(project=project, state_type_spec=spec)
    info(response)
