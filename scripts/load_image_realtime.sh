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

source $SCRIPT_DIR/get_host_ip.sh
if [ $? -ne 0 ]; then
  echo "Error retrieving HOST_IP. Exiting..."
  exit 1
fi

python sightwire realtime load \
--input $COMPAS_DATA_ROOT/realtime/oi_survey_1648/ \
--base-url http://$HOST_IP:8081 \
--vol-map $COMPAS_DATA_ROOT:/data \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA"