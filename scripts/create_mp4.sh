#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Should be at least 1 argument and it should be a directory
if [ $# -eq 0 ]
  then
    echo "No arguments supplied.  Usage: ./create_mp4.sh /home/opts/data"
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

python sightwire convert create-video \
	--input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_L_PNG \
	--output $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/video/oi_survey_1648_color_PROSILICA_L_dm.mp4 \
	--csv $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/video/ \
	--num-images 100

python sightwire convert create-video \
	--input $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_R_PNG \
	--output $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/video/oi_survey_1648_color_PROSILICA_R_dm.mp4 \
	--csv $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/video/ \
	--num-images 100
