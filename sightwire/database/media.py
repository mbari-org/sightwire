# sightwire, Apache-2.0 license
# Filename: database/media.py
# Description:  Database operations related to media
from dataclasses import asdict
import hashlib
import time
from pathlib import Path
from uuid import uuid1
import tator
from tator.openapi.tator_openapi import TatorApi, CreateListResponse
from sightwire.database.data_types import PLATFORM_LIST, CAMERA_LIST, SIDE_LIST, enum_to_string
from sightwire.logger import err, info, debug


def local_md5_partial(fname, max_chunks=5):
    """ Computes md5sum-based fingerprint of the first part of a local file.

    :param fname: Path to the local file.
    :param max_chunks: Maximum number of chunks to download.
    :returns: md5 sum of the first part of the file.
    """
    CHUNK_SIZE = 2 * 1024 * 1024
    chunk_count = 0
    md5 = hashlib.md5()

    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            if chunk:
                chunk_count += 1
                md5.update(chunk)
            if chunk_count >= max_chunks:
                break

    return md5.hexdigest()


def gen_spec(file_loc: str, type_id: int, section: str, **kwargs) -> dict:
    """
    Generate a media spec for Tator
    :param file_loc: file location
    :param type_id: media type ID
    :param section: section to assign to the media - this corresponds to a Tator section which is a collection, akin to a folder.
    :return: The media spec
    """
    file_load_path = Path(file_loc)
    attributes = {}
    data = kwargs.get('data')
    base_url = kwargs.get('base_url')  # The base URL to the file if hosted. If None, the file will be uploaded.
    if data:
        attributes = asdict(data)#, dict_factory=enum_to_string)

    if base_url:
        # Only keep the path past the compas directory
        # TODO: the /data path should be put into a config/env variable
        file_loc_sans_root = file_loc.split('data/')[-1]
        #file_url = f'http://host.docker.internal/compas/{file_loc_sans_root}' # on mac only
        file_url = f'http://172.17.0.1:8080/compas/{file_loc_sans_root}'
        debug(f'spec file URL: {file_url}')
        spec = {
            'type': type_id,
            'url': file_url,
            'name': file_load_path.name,
            'section': section,
            'md5': local_md5_partial(file_loc),
            'size': file_load_path.stat().st_size,
            'attributes': attributes,
            'gid': str(uuid1()),
            'uid': str(uuid1()),
            'reference_only': 1,
        }
    else:
        debug(f'spec file path: {file_loc}')
        spec = {
            'type': type_id,
            'path': file_loc,
            'section': section,
            'md5': local_md5_partial(file_loc),
            'size': file_load_path.stat().st_size,
            'attributes': attributes,
            'gid': str(uuid1()),
            'uid': str(uuid1()),
            'reference_only': 0,
        }

    return spec


def load_bulk(project_id: int, api: tator.api, fast_load: bool, spec) -> any:
    """
    Bulk load media into Tator. If fast_load is True, the media will be loaded asynchronously.
    :param project_id: The project ID
    :param api: The Tator API object.
    :param fast_load: If True, the media will be loaded asynchronously.
    :param spec: The media spec to create
    """
    try:
        if fast_load:
            api.create_media_list(project_id, body=spec, async_req=False)
        else:
            response = api.create_media_list(project_id, body=[spec])
            # Error if the response is not a CreateListResponse object
            if not isinstance(response, CreateListResponse):
                raise Exception(response)
            return response.id[0]
    except Exception as e:
        if 'ApplyResult' in str(e):  # This happens with async_req=False; database entry work though. Tator BUG?
            return None
        err(f'Error uploading {e}')
        return None


def upload(project_id: int, api: tator.api, type_id: int, file_load_path: Path, **kwargs) -> int:
    """
    Create a media object in Tator. If a base URL is provided, the file will be referenced. If only a file path is provided, the file will be uploaded.
    :param project_id: The project ID
    :param api: The Tator API object.
    :param type_id: The media type ID
    :param spec: The media spec to create
    :return: The media ID of the created media object, or None if the upload failed or the loading is asynchronous.
    """
    section = kwargs.get('section', 'All Media')
    attributes = kwargs.get('attributes', {})

    try:
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
        return None

    media_id = None
    while True:
        response = api.get_media_list(project_id, name=file_load_path.name)
        info(f'Waiting for transcode of {file_load_path.as_posix()}...')
        time.sleep(5)
        if len(response) == 0:
            continue
        if response[0].media_files is None:
            continue
        if response[0].id is not None:
            media_id = response[0].id
            break

    return media_id


def create_types(tator_api: TatorApi, project: int) -> None:
    """
    Create the media types in the project. Only needs to be done once and fails if the types already exist.
    :param tator_api: :class:`TatorApi` object
    :param project: Project ID
    :return:
    """

    media_types = tator_api.get_media_type_list(project=project)
    info(f"Found {len(media_types)} existing media types")
    assert len(media_types) == 0

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
                "name": "side",
                "dtype": "enum",
                "visible": True,
                "choices": SIDE_LIST,
                "labels": SIDE_LIST,
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
                "name": "side",
                "dtype": "enum",
                "visible": True,
                "choices": SIDE_LIST,
                "labels": SIDE_LIST,
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
