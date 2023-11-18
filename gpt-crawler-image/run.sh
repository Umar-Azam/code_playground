#!/bin/bash

# Check if there is a Docker image named "crawler"
if ! sudo docker images | grep -w 'crawler' > /dev/null; then
    echo "Docker repository 'crawler' not found. Building the image..."
    # Build the Docker image with the name 'crawler'
    sudo docker build -t crawler .
else
    echo "Docker image already built."
fi

sudo docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock crawler bash
