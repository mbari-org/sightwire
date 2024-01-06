#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../../.." )" && pwd )"

# The first argument is the mount point
if [ -z "$1" ]; then
  echo "Usage: $0 <mount point>"
  exit 1
fi

# Check if the mount point exists
if [ ! -d "$1" ]; then
  echo "Mount point $1 does not exist"
  exit 1
fi

# Set environment variables for customizing the docker image
export COMPAS_DIR=$1
export SCRIPT_DIR=$SCRIPT_DIR
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# If the tator directory does not exists, then clone it
if [ ! -d "$SCRIPT_DIR/tator" ]; then
  # Clone the tator repository with submodules
  git clone --recurse-submodules https://github.com/cvisionai/tator $BASE_DIR/tator
# This cb7e29084d341cbf9cceb61fdd7ef367646925f2 is the commit hash for the tator
# version on mantis.shore.mbari.org; latest version of tator is ok for development
#  cd $BASE_DIR/tator &&  git checkout cb7e29084d341cbf9cceb61fdd7ef367646925f2 --recurse-submodules
fi

# Copy docker setup files
cp $SCRIPT_DIR/nginx.conf.template $BASE_DIR/tator/nginx.conf.template
cp $SCRIPT_DIR/compose.yaml $BASE_DIR/tator/compose.yaml
cp $SCRIPT_DIR/Dockerfile.nginx $BASE_DIR/tator/Dockerfile.nginx
cp $BASE_DIR/tator/example-env $BASE_DIR/tator/.env

# Bring up the tator docker containers with the new environment
cd $BASE_DIR/tator && make tator