#!/usr/bin/env bash
# Capture a live stream and save images timestamped with the current time
# This is useful for testing real-time image capture from LCM messages
# Usage: ./capture_livestream.sh
#set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$BASE_DIR
COMPAS_DATA_ROOT=/Users/dcline/data

# Get the local host IP address in the 192 range, excluding the 255 subnet
HOST_IP=$(ifconfig | tail -n +2 | grep -o '192\.168\.[0-9]\+\.[0-9]\+' | grep -v '192\.168\.0\.255' | grep -v '^$')
# Make sure we can reach it, otherwise use fail
rc=$(curl -s -o /dev/null $HOST_IP)
if [ $rc -ne 0 ]; then
  echo "Cannot reach $HOST_IP"
  exit 1
fi

OUTPUT_DIR_LEFT=$COMPAS_DATA_ROOT/realtime/oi_survey_1648/P_L_PNG
OUTPUT_DIR_RIGHT=$COMPAS_DATA_ROOT/realtime/oi_survey_1648/P_R_PNG
# Capture a live stream and save images timestamped with the current time
python sightwire realtime capture -u rtmp://$HOST_IP:1935/streaml -o $OUTPUT_DIR_LEFT &
python sightwire realtime capture -u rtmp://$HOST_IP:1935/streamr -o $OUTPUT_DIR_RIGHT &