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

# Build and run the containers
echo "Building and starting the containers..."
docker-compose up --build -d

# Wait for 7 minutes before checking the app status
echo "Waiting for 7 minutes before checking the app status..."
sleep 240  # 4 minutes

# Retry logic to check if the app is up
for i in {1..30}; do  # 30 attempts
    # Make a request to the Streamlit app URL (modify the endpoint if needed)
    if curl --insecure --silent --head "$APP_URL" | grep "200 OK" > /dev/null; then
        echo "The app is now accessible at: $APP_URL"
        exit 0
    fi
    echo "Waiting for the app to be ready... attempt $i"
    sleep 10  # Wait 10 seconds before checking again
done

echo "Error: The app did not start successfully after 5 minutes of checking."
exit 1