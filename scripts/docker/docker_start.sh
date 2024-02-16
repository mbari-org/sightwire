#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../../.." )" && pwd )"

# Set environment variables for customizing the docker image
export SCRIPT_DIR=$SCRIPT_DIR
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# If the tator directory does not exists, then clone it
if [ ! -d "$SCRIPT_DIR/tator" ]; then
  # Clone the tator repository with submodules
  git clone --recurse-submodules https://github.com/cvisionai/tator $BASE_DIR/tator
fi

# Copy docker setup files
cp $SCRIPT_DIR/nginx.conf  $BASE_DIR/tator/
cp $SCRIPT_DIR/compose.yaml $BASE_DIR/tator/
cp $SCRIPT_DIR/Makefile $BASE_DIR/tator/
# Overwrite the media.py file with the custom one
cp $SCRIPT_DIR/media.py $BASE_DIR/tator/api/main/rest/media.py
if [ ! -e  "$BASE_DIR/tator/.env" ]; then
  cp $SCRIPT_DIR/example-env $BASE_DIR/tator/.env
fi

# Bring up the tator docker containers with the new environment
cd $BASE_DIR/tator && make tator
