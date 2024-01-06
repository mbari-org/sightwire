#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Should be at least 1 argument and it should be a directory
if [ $# -eq 0 ]
  then
    echo "No arguments supplied.  Usage: ./create_mp4.sh /mnt/compas"
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

export PYTHONPATH=$PYTHONPATH:$BASE_DIR
cd $BASE_DIR

python sightwire create-video --input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_L --output $BASE_DIR/tests/data/compas/images/oi_survey_1648_color_PROSILICA_LEFT_dm.mp4 --num-images 60
python sightwire create-video --input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_R --output $BASE_DIR/tests/data/compas/images/oi_survey_1648_color_PROSILICA_RIGHT_dm.mp4 --num-images 60
python sightwire create-video --input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/color/FLIR_LEFT --output $BASE_DIR/tests/data/compas/images/oi_survey_2115_color_FLIR_LEFT_dm.mp4 --num-images 60
python sightwire create-video --input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/color/FLIR_RIGHT --output $BASE_DIR/tests/data/compas/images/oi_survey_2115_color_FLIR_RIGHT_dm.mp4 --num-images 60
python sightwire create-video --input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_1913/color/FLIR_LEFT --output $BASE_DIR/tests/data/compas/images/oi_survey_1913_color_FLIR_LEFT_dm.mp4 --num-images 60
python sightwire create-video --input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_1913/color/FLIR_RIGHT --output $BASE_DIR/tests/data/compas/images/oi_survey_1913_color_FLIR_RIGHT_dm.mp4 --num-images 60
