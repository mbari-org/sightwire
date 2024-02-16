#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$BASE_DIR

# Should be at least 2 arguments
if [ ! $# -eq 2 ]
  then
    echo "No arguments supplied.  Usage: ./load_image.sh localhost /home/ops/data"
    exit 1
fi

if [ ! -d "$2" ]; then
  echo "Directory $2 does not exist"
  exit 1
fi

#
# On MacOSX, may need to set the path to FFMPEG, e.g. export IMAGEIO_FFMPEG_EXE=/opt/homebrew/bin/ffmpeg
#
HOST_NAME=$1
COMPAS_DATA_ROOT=$2
cd $BASE_DIR

# The csv is generated from the LCM log. See scripts/extract_log.sh for an example 

python sightwire load image \
--input-left $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_L_PNG \
--input-right $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_R_PNG \
--base-url http://$HOST_NAME:8080/compas/ \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA" \
--log-position $BASE_DIR/data/logs/oi_survey_1648_USBL_WINFROG.csv \
--log-depth $BASE_DIR/data/logs/oi_survey_1648_DEPTH_KEARFOTT_COMPAS.csv \
--max-images 1000 --bulk --force
