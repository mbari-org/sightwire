# sightwire, Apache-2.0 license
# Filename: database/data_types.py
# Description:  Database types

import enum

from datetime import datetime
from dataclasses import dataclass


# Add enum for the platform type - put this in sections
class Platform(enum.Enum):
    MINI_ROV = 'MINI ROV'
    MOLA = 'MOLA'
    LASS = 'LASS'


# Add enum for the camera type - put this in sections
class Camera(enum.Enum):
    FLIR = 'FLIR'
    STEREOPI = 'STEREOPI'
    PROSILICA = 'PROSILICA'


@dataclass
class VideoData:
    iso_start_datetime: datetime
    iso_end_datetime: datetime
    platform: Platform
    camera: Camera
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
    mission: str
    latitude: float
    longitude: float
    depth: float


# TODO: do we need this? Is there something to retain like the timestamps which may differ?
@dataclass
class StereoImageData:
    iso_datetime: datetime
    platform: Platform
    camera: Camera
    mission: str
    latitude: float
    longitude: float
    depth: float
