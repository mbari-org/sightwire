#!/usr/bin/env bash
# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../../.." )" && pwd )"

# The first argument is the volume mount point
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

# Stop tator docker containers
cd $BASE_DIR/tator && make clean