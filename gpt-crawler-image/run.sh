#!/bin/bash

# Check if there is a Docker image named "minimal"
if ! sudo docker images | grep -w 'minimal' > /dev/null; then
    echo "Docker repository 'minimal' not found. Building the image..."
    # Build the Docker image with the name 'minimal'
    sudo docker build -t minimal .
else
    echo "Docker image already built."
fi

sudo docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock minimal bash
