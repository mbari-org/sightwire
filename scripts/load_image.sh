#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$BASE_DIR

# Should be at least 1 argument and it should be a directory
if [ $# -eq 0 ]
  then
    echo "No arguments supplied.  Usage: ./load_image.sh /mnt/compas"
    exit 1
fi

if [ ! -d "$1" ]; then
  echo "Directory $1 does not exist"
  exit 1
fi

#
# On MacOSX, may need to set the path to FFMPEG, e.g. export IMAGEIO_FFMPEG_EXE=/opt/homebrew/bin/ffmpeg
#
COMPAS_DATA_ROOT=$1

cd $BASE_DIR

python sightwire load image \
--input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/stereopi \
--platform-type "MINI ROV" \
--mission-name "oi_survey_2115" \
--camera-type "STEREOPI" \
--log-depth $BASE_DIR/data/logs/oi_survey_2115_COMPAS_DEPTH.csv \
--log-position $BASE_DIR/data/logs/oi_survey_2115_MINIROV_USBL_LATLONG.csv \
--max-images 2 --force true


python sightwire load image \
--input-left $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/color/FLIR_LEFT \
--input-right $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/color/FLIR_RIGHT \
--platform-type "MINI ROV" \
--mission-name "oi_survey_2115" \
--camera-type "FLIR" \
--log-depth $BASE_DIR/data/logs/oi_survey_2115_COMPAS_DEPTH.csv \
--log-position $BASE_DIR/data/logs/oi_survey_2115_MINIROV_USBL_LATLONG.csv \
--max-images 2 --force true


python sightwire load image \
--input-left $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_L \
--input-right $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_R \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA" \
--log-depth $BASE_DIR/data/logs/oi_survey_1648_DEPTH_KEARFOTT_COMPAS.csv \
--log-position $BASE_DIR/data/logs/oi_survey_1648_USBL_WINFROG.csv \
--max-images 2 --force true


python sightwire load image \
--input-left $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_1913/color/FLIR_LEFT \
--input-right $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_1913/color/FLIR_RIGHT \
--platform-type "MINI ROV" \
--mission-name "oi_survey_1913" \
--camera-type "FLIR" \
--log-depth $BASE_DIR/data/logs/oi_survey_1913_COMPAS_DEPTH.csv \
--log-position $BASE_DIR/data/logs/oi_survey_1913_MINIROV_USBL_LATLONG.csv \
--max-images 2 --force true