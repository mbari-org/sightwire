#!/usr/bin/env bash
# Create a watchdog to check for png images in a directory
# and queue to a REDIS timeseries queue
# This is useful for testing watchdog based loads
# Usage: ./run_watchdog.sh
#set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

COMPAS_DATA_ROOT=/Users/dcline/data
export PYTHONPATH=$PYTHONPATH:$BASE_DIR
python sightwire realtime run_watchdog --input $COMPAS_DATA_ROOT/realtime/oi_survey_1648/