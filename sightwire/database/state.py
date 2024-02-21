# sightwire, Apache-2.0 license
# Filename: database/state.py
# Description: State type functions
from tator.openapi.tator_openapi import TatorApi

from sightwire.database.data_types import PLATFORM_LIST, CAMERA_LIST, SIDE_LIST
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
    image_media_type = [media_type for media_type in media_types if media_type.name == "Image"]
    assert len(image_media_type) == 1
    info(f"Found {len(media_type_ids)} media types")

    # Create the localization-associated state type an associate to both Image and Video media types
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

    # Create the Stereo state type an associate to the Image media type
    spec = {
        "name": "Stereo",
        "description": "Stereo state type for associating images generated from a stereo camera",
        "dtype": "state",
        "association": "Media",
        "visible": True,
        "grouping_default": False,
        "media_types": [image_media_type[0].id],
         "attribute_types": [
            {
                "name": "iso_datetime",
                "dtype": "datetime",
                "visible": True,
            },
            {
                "name": "depth",
                "dtype": "float",
                "visible": True,
            },
            {
                "name": "latitude",
                "dtype": "float",
                "visible": True,
                "default": 0.0
            },
            {
                "name": "longitude",
                "dtype": "float",
                "visible": True,
                "default": 0.0
            },
            {
                "name": "platform",
                "dtype": "enum",
                "visible": True,
                "default": "MINI_ROV",
                "choices": PLATFORM_LIST,
                "labels": PLATFORM_LIST
            },
            {
                "name": "camera",
                "dtype": "enum",
                "visible": True,
                "choices": CAMERA_LIST,
                "labels": CAMERA_LIST
            },
            {
                "name": "mission",
                "dtype": "string",
                "visible": True,
            }
        ]
    }

    response = tator_api.create_state_type(project=project, state_type_spec=spec)
    info(response)