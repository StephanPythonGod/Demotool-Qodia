#!/bin/bash
# Shell script to set up Qodia-Kodierungstool with persistent environment variable and interactive deployment choice

# Step 1: Define and check the repository directory environment variable
repoEnvVar="QODIA_REPO_PATH"

if [ -z "${!repoEnvVar}" ]; then
    read -p "Enter the directory where you want to clone the repository: " repo_dir
    echo "export $repoEnvVar=$repo_dir" >> ~/.bashrc
    source ~/.bashrc
    echo "Repository path saved to environment variable $repoEnvVar."
else
    repo_dir="${!repoEnvVar}"
    echo "Using existing repository path from environment variable: $repo_dir"
fi

# Step 2: Ensure the "models" directory exists
if [ ! -d "$repo_dir/models" ]; then
    echo "'models' directory does not exist. Creating it..."
    mkdir "$repo_dir/models"
    echo "'models' directory created."
else
    echo "'models' directory already exists."
fi

# Step 3: Create .env file with required environment variables if it doesn't exist
if [ ! -f "$repo_dir/.env" ]; then
    echo ".env file not found. Creating .env file..."
    read -p "Enter API Key: " api_key
    read -p "Enter API URL: " api_url
    read -p "Enter Rapid API Key: " rapid_api_key

    cat <<EOF > "$repo_dir/.env"
DEPLOYMENT_ENV=local
API_KEY=${api_key}
API_URL=${api_url}
RAPID_API_KEY=${rapid_api_key}
EOF
    echo ".env file created with environment variables."
else
    echo ".env file already exists."
fi

# Step 4: Prompt the user to choose a deployment method
echo "Choose deployment method: Enter '1' for Docker or '2' for Python"
read -r deploymentChoice
if [ "$deploymentChoice" == "1" ]; then
    # Docker Deployment
    echo "You chose Docker deployment."

    # Check for Docker and Docker Compose, prompt to install if missing
    if ! command -v docker &> /dev/null; then
        echo "Docker is not installed. Do you want to install it using apt-get? (y/n)"
        read -r installDocker
        if [ "$installDocker" == "y" ]; then
            sudo apt-get update && sudo apt-get install -y docker.io docker-compose
        else
            exit 1
        fi
    fi
    sudo systemctl start docker
    echo "Docker service started."

    # Run Docker setup script
    cd "$repo_dir" || exit
    echo "Running Docker setup script..."
    bash scripts/setup_docker.sh

elif [ "$deploymentChoice" == "2" ]; then
    # Python Deployment
    echo "You chose Python deployment."

    # Check for Python, Poetry, and Tesseract
    for cmd in python3 poetry tesseract; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "$cmd is not installed. Do you want to install it using apt-get? (y/n)"
            read -r installCmd
            if [ "$installCmd" == "y" ]; then
                sudo apt-get install -y "$cmd"
            else
                exit 1
            fi
        fi
    done

    # Run Python setup script
    cd "$repo_dir" || exit
    echo "Running Python setup script..."
    bash scripts/setup_python.sh
