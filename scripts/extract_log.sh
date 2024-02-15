#!/usr/bin/env bash
# example_gen_log.sh
# Run with ./extract_log.sh /mnt/compas
# Creates two csv files from a lcm log with depth and position data
# This is needed to create the metadata for the compas dataset for bulk loading into the database
# Modify as needed for your specific use case
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Should be at least 1 argument and it should be a directory
if [ $# -eq 0 ]
  then
    echo "No arguments supplied.  Usage: ./extract_log.sh /mnt/compas"
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

python sightwire extract-log \
--log $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/lcmlog.00 \
--usbl-channel LASS_USBL_LATLONG  \
--depth-channel LASS_DEPTH \
--output $BASE_DIR/data/logs \
--prefix oi_survey_1648

python sightwire extract-log \
--log $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/lcmlog.00 \
--usbl-channel LASS_USBL_LATLONG  \
--depth-channel LASS_DEPTH \
--output $BASE_DIR/data/logs \
--prefix oi_survey_1648