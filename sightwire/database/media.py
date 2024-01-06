# sightwire, Apache-2.0 license
# Filename: database/media.py
# Description:  Database operations related to media

from dataclasses import asdict
import tempfile
import time
from pathlib import Path
import requests

import tator
from tator.openapi.tator_openapi import TatorApi

from sightwire.database.data_types import VideoData, Platform, ImageData, StereoImageData, enum_to_string, Camera
from sightwire.logger import err, info, debug


def create_upload(project: int, file_loc: str, type_id: int, section: str, api: tator.api, data: any) -> int:
    """
    Create a media object in Tator and upload the file if it is a local file (not a URL).
    :param project:
    :param file_loc: file location
    :param type_id: media type ID
    :param section: section to assign to the media - this corresponds to a Tator section which is a collection, akin to a folder.
    :param api: The Tator API object.
    :param data: The media id
    :return:
    """
    with tempfile.TemporaryDirectory() as temp_dir:

        if 'http' in file_loc:
            file_load_path = Path(file_loc)

            try:
                response = requests.get(file_loc)
                file_load_path = Path(file_loc)
                file_load_path = Path(temp_dir) / file_load_path.name
                with open(file_load_path.as_posix(), 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                err(f'Could not download {file_loc} to {file_load_path}')
                raise e
        else:
            file_load_path = Path(file_loc)

        try:
            attributes = {}
            if data:
                attributes = asdict(data)#, dict_factory=enum_to_string)
            if 'http' in file_loc:
                for progress, response in tator.util.import_media(api,
                                                                  type_id,
                                                                  file_loc,
                                                                  section=section,
                                                                  attributes=attributes,
                                                                  fname=file_load_path.name):
                    info(f"Creating progress: {progress}%")
                    debug(response.message)
            else:
                # https://github.com/cvisionai/tator-py/blob/1cb7b2a41fab6c2eb95af603004e3c5873e8539d/tator/util/upload_media.py
                for progress, response in tator.util.upload_media(api,
                                                                  section=section,
                                                                  attributes=attributes,
                                                                  type_id=type_id,
                                                                  fname=file_load_path.name,
                                                                  path=file_load_path.as_posix()):
                    info(f"Upload progress: {progress}%")
                    debug(response)
        except Exception as e:
            if 'list' not in str(e):  # Skip over 'list' object has no attribute 'items' error
                err(f'Error uploading {file_load_path}: {e}')

        media_id = None
        while True:
            response = api.get_media_list(project, name=file_load_path.name)
            info(f'Waiting for transcode of {file_load_path.as_posix()}...')
            time.sleep(5)
            if len(response) == 0:
                continue
            if response[0].media_files is None:
                continue

            # For video
            # have_streaming = response[0].media_files.streaming is not None
            # have_archival = response[0].media_files.archival is not None
            # if have_streaming and have_archival:
            #     media_id = response[0].id
            #     break
            # For image
            if response[0].id is not None:
                media_id = response[0].id
                break

        return media_id

def create_image(project: int, api: tator.api, data: ImageData, file_loc: str, type_id: int = 1, section: str = "All Media") -> int:
    """
    Create an image object in Tator.
    :param: project The project ID
    :param api: The Tator API object.
    :param data:  The metadata for the media object.:param file_loc: The location of the file. If a path, the file will be uploaded to Tator. If a URL, the file will be referenced.
    :param type_id: The media type ID
    :param media_id: The media ID. If None, a new media object will be created. If not None, the object will be updated.
    :param section: The section to assign to the media - this corresponds to a Tator section which is a collection, akin to a folder.
    :return: The created media object.
    """
    # TODO: check if the image already exists and if so, update it
    return create_upload(project, file_loc, type_id, section, api, data)

def create_stereo_image(project: int, api: tator.api, data: StereoImageData, file_loc: str, type_id: int = 1, section: str = "All Media") -> int:
    """
    Create a reference stereo image object in Tator.
    :param: project The project ID
    :param api: The Tator API object.
    :param data:  The metadata for the media object.:param file_loc: The location of the file. If a path, the file will be uploaded to Tator. If a URL, the file will be referenced.
    :param type_id: The media type ID
    :param media_id: The media ID. If None, a new media object will be created. If not None, the object will be updated.
    :param section: The section to assign to the media - this corresponds to a Tator section which is a collection, akin to a folder.
    :return: The created media object.
    """
    # TODO: check if the image already exists and if so, update it
    return create_upload(project, file_loc, type_id, section, api, data)


def create_video(project: int, api: tator.api, data: VideoData, file_loc: str, type_id: int = 1, section: str = "All Media") -> int:
    """
    Create a media object in Tator.
    :param project:
    :param api: The Tator API object.
    :param data: The metadata for the media object.
    :param file_loc: The location of the file. If a path, the file will be uploaded to Tator. If a URL, the file will be referenced.
    :param type_id: The media type ID
    :param media_id: The media ID. If None, a new media object will be created. If not None, the object will be updated.
    :param section: The section to assign to the media - this corresponds to a Tator section which is a collection, akin to a folder.
    :return: The media ID of the created media object.
    """
    # TODO: check if the video already exists and if so, update it
    return create_upload(project, file_loc, type_id, section, api, data)


def create_types(tator_api: TatorApi, project: int) -> None:
    """
    Create the media types in the project. Only needs to be done once and fails if the types already exist.
    :param tator_api: :class:`TatorApi` object
    :param project: Project ID
    :return:
    """

    media_types = tator_api.get_media_type_list(project=project)
    # info(f"Found {len(media_types)} existing media types")
    # assert len(media_types) == 0

    spec = {
        "name": "Video",
        "description": "Video media object type",
        "dtype": "video",
        "visible": True,
        "attribute_types": [
            {
                "name": "iso_start_datetime",
                "dtype": "datetime",
                "visible": True,
            },
            {
                "name": "iso_end_datetime",
                "dtype": "datetime",
                "visible": True,
            },
            {
                "name": "platform",
                "dtype": "enum",
                "visible": True,
                "default": "MINI_ROV",
                "choices": ["MINI_ROV", "MOLA", "LASS"],
                "labels": ["MINI_ROV", "MOLA", "LASS"]
            },
            {
                "name": "camera",
                "dtype": "enum",
                "visible": True,
                "choices": ["FLIR", "STEREOPI", "PROSILICA"],
                "labels": ["FLIR", "STEREOPI", "PROSILICA"]
            },
            {
                "name": "mission",
                "dtype": "string",
                "visible": True,
            }
        ]
    }

    api_response = tator_api.create_media_type(project=project, media_type_spec=spec)
    info(f'Created Video type {api_response}')

    spec = {
        "name": "StereoVideo",
        "description": "Stereo video pair media object type",
        "dtype": "multi",
        "visible": True,
        "attribute_types": [
            {
                "name": "iso_start_datetime",
                "dtype": "datetime",
                "visible": True,
            },
            {
                "name": "iso_end_datetime",
                "dtype": "datetime",
                "visible": True,
            },
            {
                "name": "platform",
                "dtype": "enum",
                "visible": True,
                "default": "MINI_ROV",
                "choices": ["MINI_ROV", "MOLA", "LASS"],
                "labels": ["MINI_ROV", "MOLA", "LASS"]
            },
            {
                "name": "camera",
                "dtype": "enum",
                "visible": True,
                "choices": ["FLIR", "STEREOPI", "PROSILICA"],
                "labels": ["FLIR", "STEREOPI", "PROSILICA"]
            },
            {
                "name": "mission",
                "dtype": "string",
                "visible": True,
            }
        ]
    }

    api_response = tator_api.create_media_type(project=project, media_type_spec=spec)
    info(f'Created StereoVideo type {api_response}')

    spec = {
        "name": "Image",
        "description": "Image media object type",
        "dtype": "image",
        "visible": True,
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
                "default": 36.6484
            },
            {
                "name": "longitude",
                "dtype": "float",
                "visible": True,
                "default": 121.8969
            },
            {
                "name": "platform",
                "dtype": "enum",
                "visible": True,
                "default": "MINI_ROV",
                "choices": ["MINI_ROV", "MOLA", "LASS"],
                "labels": ["MINI_ROV", "MOLA", "LASS"]
            },
            {
                "name": "camera",
                "dtype": "enum",
                "visible": True,
                "choices": ["FLIR", "STEREOPI", "PROSILICA"],
                "labels": ["FLIR", "STEREOPI", "PROSILICA"]
            },
            {
                "name": "mission",
                "dtype": "string",
                "visible": True,
            }
        ]
    }

    api_response = tator_api.create_media_type(project=project, media_type_spec=spec)
    info(f'Created Image type {api_response}')

    spec = {
        "name": "StereoImage",
        "description": "Stereo image media object type",
        "dtype": "image",
        "visible": True,
        "attribute_types" : [
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
                "default": 36.6484
            },
            {
                "name": "longitude",
                "dtype": "float",
                "visible": True,
                "default": 121.8969
            },
            {
                "name": "left_id",
                "dtype": "int",
                "visible": True,
            },
            {
                "name": "right_id",
                "dtype": "int",
                "visible": True,
            },
            {
                "name": "platform",
                "dtype": "enum",
                "visible": True,
                "default": "MINI_ROV",
                "choices": ["MINI_ROV", "MOLA", "LASS"],
                "labels": ["MINI_ROV", "MOLA", "LASS"]
            },
            {
                "name": "camera",
                "dtype": "enum",
                "visible": True,
                "choices": ["FLIR", "STEREOPI", "PROSILICA"],
                "labels": ["FLIR", "STEREOPI", "PROSILICA"]
            },
            {
                "name": "mission",
                "dtype": "string",
                "visible": True,
            }
        ]
    }

    api_response = tator_api.create_media_type(project=project, media_type_spec=spec)
    info(f'Created StereoImage type {api_response}')
