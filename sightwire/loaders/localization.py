# sightwire, Apache-2.0 license
# Filename: loaders/load_localizations.py
# Description: Load localizations into the database
from pathlib import Path

import click

import common_args
from database.common import init_api_project, find_media_type
from database.data_types import Platform, Camera
from logger import info, err


@click.command("box", help="Load localization box associated with an image into the database")
@common_args.host
@common_args.token
@common_args.project
@common_args.force
@click.option("--input", '-i', type=Path, help='path to the image directory or a single image file')
@click.option("--boxes", '-b', type=Path, help='path to the detections associated with the single image file')
@click.option("--base-url", '-u', type=str, help='base url to the images, e.g. http://localhost:8000/compas/')
@click.option("--input", '-i', type=Path, help='path to the image directory or a single image file')
@click.option("--log-depth", type=Path,
              help='path to the log with exported compass datetime/depth from the lcm logs')
@click.option("--log-position", type=Path,
              help='path to the log with exported USBL datetime/lat/lon from the lcm logs')
@click.option("--platform-type", type=Platform, default=Platform.MINI_ROV, required=True)
@click.option("--camera-type", type=Camera, default=Camera.FLIR, required=True)
@click.option("--mission-name", type=str, required=True)
@click.option("--bulk", is_flag=True, help="Bulk load. CAUTION: this does not verify if the images are already loaded")
@click.option("--max-images", required=False, type=int, help="Max number of images to load")
def load_box(base_url: str, input: Path, log_depth: Path, log_position: Path,
               host: str, token: str, project: str,
               platform_type: Platform, camera_type: Camera, mission_name: str, bulk: bool,
               force: bool, max_images: int):
    """
    Load video from a local file system to the database
    :param video: Absolute path to the video to load
    :param log: Absolute path to the log with corrected timestamp/depth/lat/lon for the video frames
    :param host: Hostname, e.g. localhost
    :param token: Authentication token
    :param project: Project name to load to
    :param force: True to force load and skip over check
    :return:
    """
    image_path = input
    if image_path and not image_path.exists():
        err(f'Could not find {image_path}')
        return
    if not log_depth.exists():
        err(f'Could not find {log_depth}')
        return
    if not log_position.exists():
        err(f'Could not find {log_position}')
        return

    api, project = init_api_project(host, token, project)
    image_type = find_media_type(api, project.id, "Image")
    assert image_type is not None, f'Could not find type Image in project {project.name}'

    ste_state_type = find_state_type(api, project.id, "Stereo")
    assert ste_state_type is not None, f'Could not find type Stereo in project {project.name}'

    acceptable_extensions = ['.png', '.jpg', '.png', '.jpeg', 'tif']
    images_to_load = []
    if image_path_left:
        if image_path_left.is_dir():
            for ext in acceptable_extensions:
                new_images = sorted(image_path_left.rglob(f"*{ext}"))
                if len(new_images) > 0:
                    images_to_load.extend(new_images)
                    info(f'Found {len(new_images)} left images to load in {image_path_left} with extension {ext}')
                    break
        else:
            if image_path_left.suffix in acceptable_extensions and image_path_left.exists():
                images_to_load.append(image_path_left)

    if image_path_right:
        if image_path_right.is_dir():
            for ext in acceptable_extensions:
                new_images = sorted(image_path_right.rglob(f"*{ext}"))
                if len(new_images) > 0:
                    images_to_load.extend(new_images)
                    info(f'Found {len(new_images)} right images to load in {image_path_right} with extension {ext}')
                    break
        else:
            if image_path_right.suffix in acceptable_extensions and image_path_right.exists():
                images_to_load.append(image_path_right)

    if image_path:
        if image_path.is_dir():
            for ext in acceptable_extensions:
                new_images = sorted(image_path.rglob(f"*{ext}"))
                if len(new_images) > 0:
                    images_to_load.extend(new_images)
                    info(f'Found {len(new_images)} left images to load in {image_path} with extension {ext}')
                    break
        else:
            if image_path.suffix in acceptable_extensions and image_path.exists():
                images_to_load.append(image_path)

    if len(images_to_load) == 0:
        err(f'Could not find any images')
        return

    if max_images:
        info(f'Loading first {max_images} images')

    if force or click.confirm('Are you sure you want to load this?'
                              'You may want to check the database first to see if it is are already '
                              'loaded. Add --force to load anyway.'):

        # Search for the depth and lat/lon from the log files that is nearest to the image timestamp
        df = assign_nearest(log_depth, log_position, images_to_load, max_images)

        if df is None or len(df) == 0:
            err(f'Could not find depth and lat/lon for the images in {log_depth} and {log_position}')
            return

        section = f'{platform_type.name}/{camera_type.name}/{mission_name}'

        if bulk:
            if stereo:
                left_ids = create_media_bulk(project.id, api, df, base_url, image_type.id, section, Side.LEFT,
                                             platform_type, camera_type, mission_name)
                right_ids = create_media_bulk(project.id, api, df, base_url, image_type.id, section, Side.RIGHT,
                                              platform_type, camera_type, mission_name)
                iso_datetime = df['iso_datetime'].tolist()
                create_state_bulk(project.id, api, iso_datetime, left_ids, right_ids, ste_state_type.id, platform_type,
                                  camera_type, mission_name)
            else:
                create_media_bulk(project.id, api, df, base_url, image_type.id, section, Side.UNKNOWN, platform_type,
                                  camera_type, mission_name)
        else:
            for index, row in df.iterrows():
                if stereo:
                    left_id = create_media(project.id, api, row, base_url, image_type.id, section, Side.LEFT,
                                           platform_type, camera_type, mission_name)
                    right_id = create_media(project.id, api, row, base_url, image_type.id, section, Side.RIGHT,
                                            platform_type, camera_type, mission_name)

                    # Add the left and right images to a stereo state
                    response = api.create_state_list(
                        project=project.id,
                        body={
                            "type": ste_state_type.id,
                            "media_ids": [left_id, right_id],
                            "frame": 0,
                            "attributes": asdict(StereoImageData(
                                platform=platform_type.value,
                                camera=camera_type.value,
                                mission=mission_name,
                                iso_datetime=row.iso_datetime))
                        })
                    info(f'Created stereo state {response.id} for media LEFT {left_id} and RIGHT {right_id}')
                else:
                    create_media(project.id, api, row, base_url, image_type.id, section, Side.UNKNOWN, platform_type,
                                 camera_type, mission_name)
