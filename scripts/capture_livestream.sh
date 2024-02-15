#!/usr/bin/env bash
# Capture a live stream and save images timestamped with the current time
# This is useful for testing real-time image capture from LCM messages
# Usage: ./capture_livestream.sh localhost /path/to/left/images /path/to/right/images
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Should be exactly 3 arguments
if [ ! $# -eq 3 ]; then
    echo "No arguments supplied.  Usage: ./capture_livestream.sh localhost $PWD/tator/compas/P_R_PNG_SIM $PWD/tator/compas/P_L_PNG_SIM/"
    exit 1
fi
HOST_NAME=$1
OUTPUT_DIR_LEFT=$2
OUTPUT_DIR_RIGHT=$3

export PYTHONPATH=$PYTHONPATH:$BASE_DIR
# Useful for quick testing
#python sightwire realtime capture -u rtmp://$HOST_NAME:1935/streaml -o $OUTPUT_DIR_LEFT --max-images 100 &
#python sightwire realtime capture -u rtmp://$HOST_NAME:1935/streamr -o $OUTPUT_DIR_RIGHT --max-images 100 &
# Capture a live stream and save images timestamped with the current time
python sightwire realtime capture -u rtmp://$HOST_NAME:1935/streaml -o $OUTPUT_DIR_LEFT &
python sightwire realtime capture -u rtmp://$HOST_NAME:1935/streamr -o $OUTPUT_DIR_RIGHT &
