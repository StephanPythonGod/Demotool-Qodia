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
docker-compose up --build -d

# Wait for 7 minutes before checking the app status
Write-Host "Waiting for 7 minutes before checking the app status..."
Start-Sleep -Seconds 420  # 7 minutes

# Retry logic to check if the app is up
$attempts = 30
$app_url = Read-Host "Enter the app URL (e.g., http://localhost:8501)"

for ($i = 1; $i -le $attempts; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $app_url -Method Head -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "The app is now accessible at: $app_url" -ForegroundColor Green
            exit 0
        }
    } catch {
        Write-Host "Waiting for the app to be ready... attempt $i"
    }
    Start-Sleep -Seconds 10  # Wait 10 seconds before checking again
}

Write-Host "Error: The app did not start successfully after 5 minutes of checking." -ForegroundColor Red
exit 1
