# sightwire, Apache-2.0 license
# Filename: loaders/common.py
# Description: Common database functions
from sightwire.logger import info

from tator.openapi.tator_openapi import TatorApi
import tator


def init_api_project(host: str, token: str, project: str) -> (TatorApi, tator.models.Project):
    """
    Fetch the Tator API and project
    :param host: hostname, e.g. localhost
    :param token: api token
    :param project:  project name
    :return:
    """
    try:
        api = tator.get_api(host, token)
    except Exception as e:
        raise(e)

    info(f'Searching for project {project}.')
    tator_project = find_project(api, project)
    if tator_project is None:
        raise Exception(f'Could not find project {project}')

    info(f'Found project {tator_project.name} with id {tator_project.id}')
    return api, tator_project


def find_project(api: TatorApi, project_name: str) -> tator.models.Project:
    """
    Find the project with the given name
    :param api: :class:`TatorApi` object
    :param project_name: Name of the project
    """
    projects = api.get_project_list()
    info(f'Found {len(projects)} projects')
    for p in projects:
        if p.name == project_name:
            return p
    return None


def find_box_type(api: TatorApi, project: int) -> tator.models.LocalizationType:
    """
    Find the box type for the given project
    :param api: :class:`TatorApi` object
    :param project: project ID
    """
    types = api.get_localization_type_list(project=project)
    for t in types:
        if t.name == 'Box':
            return t
    return None


def find_state_type(api: TatorApi, project: int, type_name: str) -> tator.models.StateType:
    """
    Find the state type for the given project
    :param api: :class:`TatorApi` object
    :param project: project ID
    :param type_name: Name of the state type
    """
    types = api.get_state_type_list(project=project)
    for t in types:
        if t.name == type_name:
            return t
    return None


def find_media_type(api: TatorApi, project: int, type_name: str) -> tator.models.MediaType:
    """
    Find the media type for the given project
    :param type_name: String that identifies type, e.g. "Stereo"
    :param api: :class:`TatorApi` object
    :param project: project ID
    """
    types = api.get_media_type_list(project=project)
    for t in types:
        if t.name == type_name:
            return t
    return None
