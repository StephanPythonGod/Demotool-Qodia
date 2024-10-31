#!/bin/bash
# Shell script for Python deployment setup: installs Poppler, configures Tesseract, and adjusts PATH.

# Step 1: Define the repo directory and Poppler subfolder path
repo_dir="${QODIA_REPO_PATH:?Environment variable QODIA_REPO_PATH not set}"
poppler_dir="$repo_dir/poppler"

# Step 2: Install Poppler
if [ ! -d "$poppler_dir" ]; then
    echo "Installing Poppler..."
    
    # Determine Linux package manager and install Poppler
    if command -v apt-get &>/dev/null; then
        sudo apt-get update && sudo apt-get install -y poppler-utils
    elif command -v yum &>/dev/null; then
        sudo yum install -y poppler-utils
    else
        echo "Error: Unsupported package manager. Please install Poppler manually."
        exit 1
    fi
    echo "Poppler installed successfully."
else
    echo "Poppler is already installed."
fi

# Step 3: Configure Tesseract
# Check if Tesseract is installed
if ! command -v tesseract &>/dev/null; then
    echo "Error: Tesseract is not installed. Please install it first."
    exit 1
fi

# Determine Tesseract data directory and download German language file if missing
tessdata_dir=$(tesseract --print-parameters | grep -oP 'TESSDATA_PREFIX=\K.*')
if [ ! -f "$tessdata_dir/deu.traineddata" ]; then
    echo "Downloading German language file for Tesseract..."
    wget -P "$tessdata_dir" https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
    echo "German language file downloaded and configured for Tesseract."
else
    echo "Tesseract German language file already exists."
fi

# Step 4: Add Python user scripts directory to PATH if not present
python_scripts="$HOME/.local/bin"
if [[ ":$PATH:" != *":$python_scripts:"* ]]; then
    echo "Adding $python_scripts to PATH."
    echo "export PATH=\"$python_scripts:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc
else
    echo "$python_scripts is already in PATH."
fi

# Step 5: Navigate to the repository directory and install Poetry environment
cd "$repo_dir" || exit
echo "Initializing the Poetry environment..."
poetry install
echo "Poetry environment set up successfully."