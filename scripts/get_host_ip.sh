#!/bin/bash

# Extract the HOST_IP using ifconfig
HOST_IP=$(ifconfig | grep -Eo '192\.168\.[0-9]+\.[0-9]+' | grep -vE '192\.168\.0\.255' | head -n 1)

# Check if HOST_IP is empty
if [ -z "$HOST_IP" ]; then
  echo "Unable to determine HOST_IP."
  exit 1
fi

# Check if we can reach the HOST_IP
if ! ping -c 1 $HOST_IP &>/dev/null; then
  echo "Cannot reach $HOST_IP."
  exit 1
fi

echo "$HOST_IP"
