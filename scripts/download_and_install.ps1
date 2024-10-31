# PowerShell script to set up Qodia-Kodierungstool with persistent environment variable and interactive deployment choice

# Step 0: Set PowerShell Execution Policy (run this if permissions need updating for the session)
# Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process

# Step 1: Define and check the repository directory environment variable
$repoEnvVar = "QODIA_REPO_PATH"

if (-not (Test-Path -Path "Env:\$repoEnvVar")) {
    $repo_dir = Read-Host "Enter the directory where you want to clone the repository"
    [System.Environment]::SetEnvironmentVariable($repoEnvVar, $repo_dir, "Machine")
    Write-Host "Repository path saved to environment variable $repoEnvVar."
} else {
    $repo_dir = $env:QODIA_REPO_PATH
    Write-Host "Using existing repository path from environment variable: $repo_dir"
}

# Step 2: Ensure the "models" directory exists
$modelsDir = Join-Path -Path $repo_dir -ChildPath "models"
if (-not (Test-Path -Path $modelsDir)) {
    New-Item -Path $modelsDir -ItemType Directory | Out-Null
    Write-Host "'models' directory created."
} else {
    Write-Host "'models' directory already exists."
}

# Step 3: Create .env file with required environment variables if it doesn't exist
$envFile = Join-Path -Path $repo_dir -ChildPath ".env"
if (-not (Test-Path -Path $envFile)) {
    Write-Host ".env file not found. Creating .env file..."
    $api_key = Read-Host "Enter API Key"
    $api_url = Read-Host "Enter API URL"
    $rapid_api_key = Read-Host "Enter Rapid API Key"

    @"
DEPLOYMENT_ENV=local
API_KEY=$api_key
API_URL=$api_url
RAPID_API_KEY=$rapid_api_key
"@ | Out-File -FilePath $envFile -Encoding utf8
    Write-Host ".env file created with environment variables."
} else {
    Write-Host ".env file already exists."
}

# Step 4: Prompt the user to choose a deployment method
$deploymentChoice = Read-Host "Choose deployment method: Enter '1' for Docker or '2' for Python"
if ($deploymentChoice -eq '1') {
    # Docker Deployment
    Write-Host "You chose Docker deployment."

    # Check if Docker and Docker Compose are installed
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Docker is not installed. Please install Docker from https://docs.docker.com/get-docker/"
        exit 1
    }
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Docker Compose is not installed. Please install Docker Compose from https://docs.docker.com/compose/install/"
        exit 1
    }
    # Start Docker if not running
    Start-Service docker
    Write-Host "Docker service started."

    # Run Docker setup script
    Set-Location $repo_dir
    Write-Host "Running Docker setup script..."
    powershell.exe -ExecutionPolicy Bypass -File "scripts/setup_docker.ps1"

} elseif ($deploymentChoice -eq '2') {
    # Python Deployment
    Write-Host "You chose Python deployment."

    # Check for Python, Poetry, and Tesseract
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Python 3.12 is not installed. Please install it from https://www.python.org/downloads/"
        exit 1
    }
    # Check if Poetry is installed, if not, attempt to install it
    if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Host "Poetry is not installed. Attempting to install Poetry..."

        # Download and install Poetry using the official install script
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

        # Add %APPDATA%\Python\Scripts to PATH if not present
        $python_scripts = [System.IO.Path]::Combine($env:APPDATA, "Python\Scripts")
        if ($env:Path -notcontains $python_scripts) {
            [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $python_scripts, "Machine")
            Write-Host "%APPDATA%\Python\Scripts has been added to PATH."
            Write-Host "Please restart your PowerShell session for the changes to take effect."
        } else {
            Write-Host "%APPDATA%\Python\Scripts is already in PATH."
        }

        # Verify Poetry installation
        if (Get-Command poetry -ErrorAction SilentlyContinue) {
            Write-Host "Poetry installed successfully."
        } else {
            Write-Host "Error: Poetry installation failed. Please install it manually from https://python-poetry.org/docs/#installation."
            exit 1
        }
    } else {
        Write-Host "Poetry is already installed."
    }
    if (-not (Get-Command tesseract -ErrorAction SilentlyContinue)) {
        Write-Host "Error: Tesseract is not installed. Please install it from https://github.com/tesseract-ocr/tesseract"
        exit 1
    }
    # Run Python setup script
    Set-Location $repo_dir
    Write-Host "Running Python setup script..."
    powershell.exe -ExecutionPolicy Bypass -File "scripts/setup_python.ps1"
} else {
    Write-Host "Invalid choice. Exiting."
    exit 1
}
