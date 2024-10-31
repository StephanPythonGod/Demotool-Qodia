# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

# Check if "models" directory exists, create it if not
if (-not (Test-Path -Path "./models")) {
    Write-Host "'models' directory does not exist. Creating it..."
    New-Item -ItemType Directory -Path "./models" | Out-Null
    Write-Host "'models' directory created."
} else {
    Write-Host "'models' directory already exists."
}

# Build and run the containers
Write-Host "Building and starting the containers..."
docker-compose --env-file .env up --build -d
