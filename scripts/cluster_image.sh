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
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/sdcat

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/stereopi \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_2115/stereopi \
 --model mbari/megamidwater --scale-percent 100 --conf .1 --skip-saliency

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/color/FLIR_LEFT \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_2115/color/FLIR_LEFT \
 --model mbari/megamidwater --scale-percent 100 --conf .01 --skip-saliency

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_2115/color/FLIR_RIGHT \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_2115/color/FLIR_RIGHT \
 --model mbari/megamidwater --scale-percent 100 --conf .01 --skip-saliency

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_L \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_1648/color/PROSILICA_L \
 --model mbari/megamidwater --scale-percent 100 --conf .01 --skip-saliency

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_R \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_1648/color/PROSILICA_R \
 --model mbari/megamidwater --scale-percent 100 --conf .01 --skip-saliency

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_1913/color/FLIR_LEFT \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_1913/color/FLIR_LEFT \
 --model mbari/megamidwater --scale-percent 100 --conf .01 --skip-saliency

python sdcat.py detect \
--image-dir $COMPAS_DATA_ROOT/DATA/RAW/MBARI/MINIROV/20231110f1/images/oi_survey_1913/color/FLIR_RIGHT \
 --save-dir /Users/dcline/Desktop/compas/sdcat_out/oi_survey_1913/color/FLIR_LEFT \
 --model mbari/megamidwater --scale-percent 100 --conf .01 --skip-saliency
