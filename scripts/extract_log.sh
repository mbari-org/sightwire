#!/usr/bin/env bash
# Creates two csv files from a lcm log with depth and position data
# This is needed to create the metadata for the compas dataset for bulk loading into the database
# Modify as needed for your specific use case
# Run with ./extract_log.sh
#set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$BASE_DIR
COMPAS_DATA_ROOT=/Users/dcline/data

cd $BASE_DIR

python sightwire convert extract-log \
--log $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/lcmlog.00 \
--usbl-channel LASS_USBL_LATLONG  \
--depth-channel LASS_DEPTH \
--output $BASE_DIR/data/logs \
--prefix oi_survey_1648

python sightwire convert extract-log \
--log $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/lcmlog.00 \
--usbl-channel LASS_USBL_LATLONG  \
--depth-channel LASS_DEPTH \
--output $BASE_DIR/data/logs \
--prefix oi_survey_1648
