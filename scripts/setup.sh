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

# Prompt the user for environment variables
read -p "Enter API Key: " api_key
read -p "Enter API URL: " api_url
read -p "Enter Rapid API Key: " rapid_api_key

# Create or update the .env file
cat <<EOF > .env
DEPLOYMENT_ENV=local
API_KEY=${api_key}
API_URL=${api_url}
RAPID_API_KEY=${rapid_api_key}
EOF

echo "Environment variables saved to .env file."

# Build and run the containers with .env file passed to Docker Compose
echo "Building and starting the containers..."
docker-compose --env-file .env up --build -d
