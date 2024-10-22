# Step 1: Check if Git is installed, if not, throw an error with instructions
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Git is not installed. Please install Git from the following link:"
    Write-Host "https://git-scm.com/download/win"
    exit 1
} else {
    Write-Host "Git is already installed."
}

# Step 2: Clone the repository into the specified directory
$repo_url = "https://github.com/naibill/Qodia-Kodierungstool.git"
$repo_dir = Read-Host "Enter the directory where you want to clone the repository"
git clone $repo_url $repo_dir
Set-Location $repo_dir

# Step 3: Check if Docker is installed, if not, throw an error with instructions
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed. Please install Docker from the following link:"
    Write-Host "https://docs.docker.com/get-docker/"
    exit 1
} else {
    Write-Host "Docker is already installed."
}

# Step 4: Check if Docker Compose is installed, if not, throw an error with instructions
if (-not (docker-compose -v)) {
    Write-Host "Error: Docker Compose is not installed. Please install Docker Compose from the following link:"
    Write-Host "https://docs.docker.com/compose/install/"
    exit 1
} else {
    Write-Host "Docker Compose is already installed."
}

# Step 5: Start Docker (if not running)
Start-Service docker

# Step 6: Change directory to the cloned repo
Set-Location $repo_dir

# Step 7: Execute the setup.ps1 script
Write-Host "Running the setup script..."
powershell.exe -ExecutionPolicy Bypass -File "scripts/setup.ps1"

