#!/bin/bash

# Name of the Qdrant Docker container
CONTAINER_NAME="qdrant_personalization"

# Command-line arguments
ACTION=$1

# Start function
start_container() {
    echo "Starting Qdrant Docker container $CONTAINER_NAME..."
    docker run -d --name $CONTAINER_NAME -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
    echo "Qdrant container started with name: $CONTAINER_NAME"
}

# Stop function
stop_container() {
    echo "Stopping Qdrant Docker container $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "Qdrant container stopped and removed."
}

# Script usage
usage() {
    echo "Usage: $0 {start|stop}"
    exit 1
}

# Main logic
if [ "$ACTION" == "start" ]; then
    start_container
elif [ "$ACTION" == "stop" ]; then
    stop_container
else
    usage
fi
