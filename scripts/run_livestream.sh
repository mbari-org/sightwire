#!/usr/bin/env bash
# Create a live stream from a set of images using ffmpeg
# This is useful for testing real-time image capture
# Usage: ./run_livestream.sh
#set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Get the local host IP address in the 192 range, excluding the 255 subnet
HOST_IP=$(ifconfig | tail -n +2 | grep -o '192\.168\.[0-9]\+\.[0-9]\+' | grep -v '192\.168\.0\.255' | grep -v '^$')
# Make sure we can reach it, otherwise use fail
rc=$(curl -s -o /dev/null $HOST_IP)
if [ $rc -ne 0 ]; then
  echo "Cannot reach $HOST_IP"
  exit 1
fi

export PYTHONPATH=$PYTHONPATH:$BASE_DIR

COMPAS_DATA_ROOT=/Users/dcline/data
# The path to store streamable video files
MP4_VID_DIR=$COMPAS_DATA_ROOT/compas_live/live

mkdir -p $MP4_VID_DIR

for side in L R; do
  MP4_VID=$MP4_VID_DIR/PROSILICA_$side.mp4
  if [ ! -f $MP4_VID ]; then
    echo "Creating live streamable video $MP4_VID"
    # Create a streamable video from a set of images
    echo ffmpeg -framerate 5 \
    -pattern_type glob \
    -i $COMPAS_DATA_ROOT/DATA/RAW/MBARI/LASS/20231010d1/images/oi_survey_1648/color/PROSILICA_$side\_PNG/\*.png \
    -c:v libx264 -crf 18 -g 5 -sc_threshold 0 -hls_time 10 \
    $MP4_VID
  fi
done

# Keep looping the live stream for testing
# When this is run, the stream will be available at rtmp://localhost:1935/streaml and rtmp://localhost:1935/streamr
# Use VLC to view the stream by opening a network stream and entering the URL
MP4_VID_L=$MP4_VID_DIR/PROSILICA_L.mp4
MP4_VID_R=$MP4_VID_DIR/PROSILICA_R.mp4
while true;
do
  echo "Restarting live stream" rtmp://$HOST_IP:1935/streaml and rtmp://$HOST_IP:1935/streamr
  # Right it slightly longer, so background the left stream and wait for the right to finish to simulate sync
  ffmpeg -v error -re -i $MP4_VID_L -c copy -f flv rtmp://$HOST_IP:1935/streaml &
  ffmpeg -v error -re -i $MP4_VID_R -c copy -f flv rtmp://$HOST_IP:1935/streamr
done
