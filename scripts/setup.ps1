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

# Prompt the user for environment variables
$api_key = Read-Host "Enter API Key"
$api_url = Read-Host "Enter API URL"
$rapid_api_key = Read-Host "Enter Rapid API Key"

# Create or update the .env file
$envFileContent = @"
DEPLOYMENT_ENV=local
API_KEY=$api_key
API_URL=$api_url
RAPID_API_KEY=$rapid_api_key
"@
$envFileContent | Out-File -Encoding UTF8 .env

Write-Host "Environment variables saved to .env file."

# Build and run the containers
Write-Host "Building and starting the containers..."
docker-compose --env-file .env up --build -d
