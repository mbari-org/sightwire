#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../../.." )" && pwd )"

# Set environment variables for customizing the docker image
export SCRIPT_DIR=$SCRIPT_DIR

# If the tator directory does not exists, then clone it
if [ ! -d "$SCRIPT_DIR/tator" ]; then
  # Clone the tator repository with submodules
  git clone --recurse-submodules https://github.com/cvisionai/tator $BASE_DIR/tator
fi

# Copy docker setup files
cp $SCRIPT_DIR/nginx.conf $BASE_DIR/tator/
cp $SCRIPT_DIR/nginx_compas.conf $BASE_DIR/tator/
cp $SCRIPT_DIR/Dockerfile.nginx $BASE_DIR/tator/
cp $SCRIPT_DIR/compose.yaml $BASE_DIR/tator/
cp $SCRIPT_DIR/Makefile $BASE_DIR/tator/

# Overwrite the media.py file with the custom one
cp $SCRIPT_DIR/media.py $BASE_DIR/tator/api/main/rest/media.py
if [ ! -e  "$BASE_DIR/tator/.env" ]; then
  cp $SCRIPT_DIR/example-env $BASE_DIR/tator/.env
fi

# First build the docker image that serves any media files with nginx
# This is a custom image that has the same user and group id as the host
# which allows the container to read without permission issues
cd $BASE_DIR/tator && \
docker build -f Dockerfile.nginx -t mbari-nginx \
--build-arg USER_ID=$(id -u) \
--build-arg GROUP_ID=$(id -g) --no-cache .

# Bring up the tator docker containers with the new environment
cd $BASE_DIR/tator && make tator

# Stop the compas media server container in case it is already running
if [ "$(docker ps -q -f name=nginx_compas)" ]; then
  docker stop nginx_compas
fi

# Start the compas media server
# Modify this as needed to mount data from the host
# Use port 8081 to avoid collision with tator nginx server
# which is running on port 8080
cd $BASE_DIR/tator && \
docker run --rm -d -p 8081:8081 \
  -v /Users/dcline/data:/data \
  -v $BASE_DIR/tator/nginx_compas.conf:/etc/nginx/conf.d/default.conf \
  --name nginx_compas mbari-nginx

echo "Done"