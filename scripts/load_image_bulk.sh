#!/usr/bin/env bash
# Loads data in bulk
# This is useful for testing bulk image load
# Usage: ./load_image.sh
#set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$BASE_DIR
COMPAS_DATA_ROOT=/Users/dcline/data

source $SCRIPT_DIR/get_host_ip.sh
if [ $? -ne 0 ]; then
  echo "Error retrieving HOST_IP. Exiting..."
  exit 1
fi

python sightwire realtime capture \
--base-url http://$HOST_IP:8081
--vol-map $COMPAS_DATA_ROOT:/data \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA"