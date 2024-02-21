from dataclasses import asdict
from typing import List

import pandas as pd
import tator

from sightwire.database.data_types import Platform, Camera, StereoImageData, enum_to_string, Side, ImageData
from sightwire.database.media import gen_spec
from sightwire.logger import info, err, debug


def create_state_bulk(project_id: int, api: tator.api, iso_datetime: list, ids_left: list, ids_right: list,
                      state_type_id: int, platform: Platform, camera: Camera,
                      mission_name: str):
    """
    Create stereo states in bulk. This is used to create associations between left and right images
    that can be queried by e.g. time, mission, platform, camera, etc.
    """
    state_ids = []
    chunk_size = 500  # Number of pairs to load at a time
    num_chunks = len(ids_left) // chunk_size + (len(ids_right) % chunk_size > 0)
    frame_start = iso_datetime[0].timestamp()
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        left_chunk = ids_left[start_idx:end_idx]
        right_chunk = ids_right[start_idx:end_idx]
        specs = [{
            "type": state_type_id,
            "media_ids": [left, right],
            "frame": 0,
            "attributes": asdict(StereoImageData(
                platform=platform.value,
                camera=camera.value,
                mission=mission_name,
                iso_datetime=dt))}
            for dt, left, right in zip(iso_datetime, left_chunk, right_chunk)]
        assert specs is not None, f'Could not create specs for stereo state'
        info(f'Creating {len(specs)} stereo states')
        state_ids += [
            new_id
            for response in tator.util.chunked_create(
                api.create_state_list, project_id, chunk_size=chunk_size, body=specs
            )
            for new_id in response.id
        ]
        info(f"Created {len(state_ids)} stereo states")


def create_media_bulk(project_id: int, api: tator.api, df: pd.DataFrame, base_url: str, vol_map:dict, image_type_id: int,
                      section: str,side: Side, platform: Platform, camera: Camera, mission_name: str) -> List[int]:
    chunk_size = 500  # Number of images to load at a time
    num_chunks = len(df) // chunk_size + (len(df) % chunk_size > 0)
    media_ids = []
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        df_chunk = df.iloc[start_idx:end_idx]
        specs = None
        if side == Side.LEFT:
            specs = [gen_spec(
                file_loc=row.left,
                type_id=image_type_id,
                section=section,
                data=ImageData(
                    platform=platform.value,
                    camera=camera.value,
                    side=side.value,
                    mission=mission_name,
                    iso_datetime=row.iso_datetime,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    depth=row.depth),
                base_url=base_url, vol_map=vol_map) for key, row in df_chunk.iterrows()]
        if side == Side.RIGHT:
            specs = [gen_spec(
                file_loc=row.right,
                type_id=image_type_id,
                section=section,
                data=ImageData(
                    platform=platform.value,
                    camera=camera.value,
                    side=side.value,
                    mission=mission_name,
                    iso_datetime=row.iso_datetime,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    depth=row.depth),
                base_url=base_url, vol_map=vol_map) for key, row in df_chunk.iterrows()]
        if side == Side.UNKNOWN:
            specs = [gen_spec(
                file_loc=row.image,
                type_id=image_type_id,
                section=section,
                data=ImageData(
                    platform=platform.value,
                    camera=camera.value,
                    side=side.value,
                    mission=mission_name,
                    iso_datetime=row.iso_datetime,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    depth=row.depth),
                base_url=base_url, vol_map=vol_map) for key, row in df_chunk.iterrows()]
        assert specs is not None, f'Could not create specs for {side} images'
        media_ids += [
            new_id
            for response in tator.util.chunked_create(
                api.create_media_list, project_id, chunk_size=chunk_size, body=specs
            )
            for new_id in response.id
        ]
        info(f"Created {len(media_ids)} {side} medias")
    info(f"Created {len(media_ids)} {side} medias!")
    return media_ids


def create_media(project_id: int, api: tator.api, row: pd.Series, base_url: str, vol_map: dict, image_type_id: int, section: str,
                 side: Side, platform: Platform, camera: Camera, mission_name: str) -> int:
    image = None
    try:
        image_data = ImageData(
            platform=platform.value,
            camera=camera.value,
            side=side.value,
            mission=mission_name,
            iso_datetime=row.iso_datetime,
            latitude=row.latitude,
            longitude=row.longitude,
            depth=row.depth)
        spec = None
        if side == Side.LEFT:
            image = row.left
            spec = gen_spec(file_loc=row.left,
                            type_id=image_type_id,
                            section=section,
                            data=image_data,
                            base_url=base_url,
                            vol_map=vol_map)
        if side == Side.RIGHT:
            image = row.right
            spec = gen_spec(file_loc=row.right,
                            type_id=image_type_id,
                            section=section,
                            data=image_data,
                            base_url=base_url,
                            vol_map=vol_map)
        if side == Side.UNKNOWN:
            image = row.image
            spec = gen_spec(file_loc=row.image,
                            type_id=image_type_id,
                            section=section,
                            data=image_data,
                            base_url=base_url,
                            vol_map=vol_map)
        assert spec is not None, f'Could not create spec for {side} image'
        response = api.create_media_list(project_id, body=spec, async_req=False)
        return response.id
    except Exception as e:
        if 'ApplyResult' in str(e):
            info(f'Image {image} uploaded')
        else:
            err(f'Error uploading {e}')
            raise e
