#!/usr/bin/env bash
# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../../.." )" && pwd )"

# Set environment variables for customizing the docker image
export SCRIPT_DIR=$SCRIPT_DIR
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# Stop tator docker containers
cd $BASE_DIR/tator && make clean

# Stop the compas media server
docker stop nginx_compas