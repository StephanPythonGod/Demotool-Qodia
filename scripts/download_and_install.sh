#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check if Git is installed, if not, install Git
if ! command_exists git; then
    echo "Git not found. Installing Git..."
    sudo apt-get update -y && sudo apt-get install git -y || sudo yum install git -y
else
    echo "Git is already installed."
fi

# Step 2: Clone the repository into the specified directory
echo "Cloning the repository..."
read -p "Enter the directory where you want to clone the repository: " repo_dir
git clone https://github.com/naibill/Qodia-Kodierungstool.git "$repo_dir"
cd "$repo_dir" || exit

# Step 3: Check if Docker is installed, if not, throw an error with instructions
if ! command_exists docker; then
    echo "Error: Docker is not installed. Please install Docker from the following link:"
    echo "https://docs.docker.com/get-docker/"
    exit 1
else
    echo "Docker is already installed."
fi

# Step 4: Check if Docker Compose is installed, if not, throw an error with instructions
if ! command_exists docker-compose; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose from the following link:"
    echo "https://docs.docker.com/compose/install/"
    exit 1
else
    echo "Docker Compose is already installed."
fi

# Step 5: Start Docker service (if not already running)
sudo systemctl start docker

# Step 6: Change directory to the cloned repo
cd "$repo_dir" || exit

# Step 7: Execute the setup.sh script
echo "Running the setup script..."
chmod +x scripts/setup.sh
./scripts/setup.sh
