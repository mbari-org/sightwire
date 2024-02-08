# sightwire, Apache-2.0 license
# Filename: database/data_types.py
# Description:  Database types

import enum

from datetime import datetime
from dataclasses import dataclass


def enum_to_list(obj):
    l = list(obj)
    return [e.value for e in l]


# Add enum for the platform type - put this in sections
class Platform(enum.Enum):
    MINI_ROV = 'MINI ROV'
    MOLA = 'MOLA'
    LASS = 'LASS'


PLATFORM_LIST = enum_to_list(Platform)


# Add enum for the camera type - put this in sections
class Camera(enum.Enum):
    FLIR = 'FLIR'
    STEREOPI = 'STEREOPI'
    PROSILICA = 'PROSILICA'


# Convert the enum values to a list and extract the values for the choices to use database initialization
CAMERA_LIST = enum_to_list(Camera)


class Side(enum.Enum):
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    STEREO = 'STEREO'
    UNKNOWN = 'UNKNOWN'


SIDE_LIST = enum_to_list(Side)


@dataclass
class VideoData:
    iso_start_datetime: datetime
    iso_end_datetime: datetime
    platform: Platform
    camera: Camera
    side: Side
    mission: str


# Convert enum to string - useful with asdict
def enum_to_string(obj):
    if isinstance(obj, enum.Enum):
        return obj.name
    return obj


@dataclass
class ImageData:
    iso_datetime: datetime
    platform: Platform
    camera: Camera
    side: Side
    mission: str
    latitude: float
    longitude: float
    depth: float

@dataclass
class StereoImageData:
    iso_datetime: datetime
    platform: Platform
    camera: Camera
    mission: str
