#!/bin/bash

# Check if Docker and Docker Compose are installed
if ! [ -x "$(command -v docker)" ]; then
    echo "Error: Docker is not installed." >&2
    exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
    echo "Error: Docker Compose is not installed." >&2
    exit 1
fi

# Check if "models" directory exists, create it if not
if [ ! -d "./models" ]; then
    echo "'models' directory does not exist. Creating it..."
    mkdir ./models
    echo "'models' directory created."
else
    echo "'models' directory already exists."
fi

# Build and run the containers with .env file passed to Docker Compose
echo "Building and starting the containers..."
docker-compose --env-file .env up --build -d
