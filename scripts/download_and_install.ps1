# PowerShell script to set up Qodia-Kodierungstool with persistent environment variable

# Function to validate directory path
function Test-ValidPath {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    try {
        $null = [System.IO.Path]::GetFullPath($Path)
        return $true
    } catch {
        return $false
    }
}

# Function to validate API key format
function Test-ApiKey {
    param([string]$key)
    return -not [string]::IsNullOrWhiteSpace($key)
}

# Function to get Python command and validate version
function Get-PythonCommand {
    # First try the 'py' launcher
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            $pyVersion = (& py -3.12 --version 2>&1).ToString()
            if ($pyVersion -match 'Python 3\.12\.\d+') {
                Write-Host "Found 'py' command with Python 3.12"
                return "py -3.12"
            }
        } catch {
            Write-Host "Found 'py' command but couldn't verify version"
        }
    }
    
    # Then try 'python' command
    if (Get-Command python -ErrorAction SilentlyContinue) {
        try {
            $pythonVersion = (& python --version 2>&1).ToString()
            if ($pythonVersion -notmatch "Microsoft Store" -and 
                $pythonVersion -notmatch "was not found" -and 
                $pythonVersion -match 'Python 3\.12\.\d+') {
                Write-Host "Found 'python' command with Python 3.12"
                return "python"
            }
        } catch {
            Write-Host "Found 'python' command but couldn't verify version"
        }
    }
    
    return $null
}

# Function to attempt git clone with timeout and progress reporting
function Invoke-GitCloneWithTimeout {
    param(
        [string]$RepoUrl,
        [string]$Directory,
        [int]$TimeoutSeconds = 60
    )
    
    try {
        Write-Host "Attempting to clone repository..."
        Write-Host @"
Note: You will be prompted for GitHub credentials if needed.
For HTTPS authentication, you can use:
- Username: Your GitHub username
- Password: A GitHub Personal Access Token
"@ -ForegroundColor Yellow
        Write-Host "Timeout set to $TimeoutSeconds seconds"
        
        # Set up the clone operation
        $scriptBlock = {
            param($RepoUrl, $Directory)
            
            # Configure Git for HTTPS and Windows
            git config --global core.autocrlf true
            
            # Try the clone with progress
            $result = git clone --progress $RepoUrl $Directory 2>&1
            if ($LASTEXITCODE -eq 0) {
                return @{Success=$true; Output=$result}
            } else {
                return @{Success=$false; Output=$result}
            }
        }
        
        Write-Host "Starting clone operation..."
        $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $RepoUrl, $Directory
        
        # Wait for job with progress indicator
        $elapsed = 0
        $interval = 5  # Check every 5 seconds
        while ($elapsed -lt $TimeoutSeconds) {
            $jobState = Get-Job -Id $job.Id | Select-Object -ExpandProperty State
            Write-Host "Clone in progress... ($elapsed seconds elapsed)"
            
            if ($jobState -eq "Completed") {
                break
            }
            
            Start-Sleep -Seconds $interval
            $elapsed += $interval
        }
        
        if ($elapsed -ge $TimeoutSeconds) {
            Write-Host "Clone operation timed out after $TimeoutSeconds seconds"
            Stop-Job -Job $job
            Remove-Job -Job $job -Force
            return $false
        }
        
        $result = Receive-Job -Job $job
        Remove-Job -Job $job
        
        if ($result.Success) {
            Write-Host "Clone completed successfully in $elapsed seconds"
            Write-Host $result.Output
            return $true
        } else {
            Write-Host "Clone failed after $elapsed seconds with output:"
            Write-Host $result.Output
            return $false
        }
    }
    catch {
        Write-Error "Clone attempt failed: $_"
        return $false
    }
}

# Set PowerShell Execution Policy for the current session if needed
try {
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process -Force
} catch {
    Write-Error "Failed to set execution policy: $_"
    exit 1
}

# Verify required tools
Write-Host "Checking system requirements..."
$requiredTools = @{
    'git' = 'Git is not installed. Please install from https://git-scm.com/downloads'
}

foreach ($tool in $requiredTools.Keys) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error $requiredTools[$tool]
        exit 1
    }
}

# Check Git version
$gitVersion = (git --version) -replace 'git version '
if ([version]$gitVersion -lt [version]'2.0.0') {
    Write-Error "Git version $gitVersion is too old. Please upgrade Git."
    exit 1
}

# Display GitHub PAT instructions
Write-Host @"

Important: This script requires a GitHub Personal Access Token (PAT) for authentication.
If you haven't already:
1. Go to GitHub.com → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Generate a new token with the following permissions:
   - repo (Full control of private repositories)
   - read:org (Read org and team membership)
3. Copy the token - you'll need it when prompted during the clone operation
4. Store the token safely - you won't be able to see it again!

"@ -ForegroundColor Yellow

# Environment variable handling
$repoEnvVar = "QODIA_REPO_PATH"
$userEnvPath = [System.Environment]::GetEnvironmentVariable($repoEnvVar, "User")

if ([string]::IsNullOrWhiteSpace($userEnvPath)) {
    do {
        $repo_dir = Read-Host "Enter the directory where you want to clone the repository"
        try {
            $repo_dir = [System.IO.Path]::GetFullPath($repo_dir)
        } catch {
            Write-Host "Invalid path format. Please enter a valid directory path."
            continue
        }
    } until (Test-ValidPath $repo_dir)
    
    try {
        [System.Environment]::SetEnvironmentVariable($repoEnvVar, $repo_dir, "User")
        $env:QODIA_REPO_PATH = $repo_dir
        Write-Host "Repository path saved to environment variable $repoEnvVar."
    } catch {
        Write-Error "Failed to set environment variable: $_"
        exit 1
    }
} else {
    $repo_dir = $userEnvPath
    Write-Host "Using existing repository path from environment variable: $repo_dir"
}

# Create directory if it doesn't exist
if (-not (Test-Path -Path $repo_dir)) {
    try {
        New-Item -Path $repo_dir -ItemType Directory -Force | Out-Null
        Write-Host "Created directory: $repo_dir"
    } catch {
        Write-Error "Failed to create directory: $_"
        exit 1
    }
}

# Clone repository section
if (-not (Test-Path -Path (Join-Path $repo_dir ".git"))) {
    $maxRetries = 3
    $currentTry = 0
    $success = $false
    
    while (-not $success -and $currentTry -lt $maxRetries) {
        $currentTry++
        Write-Host "Clone attempt $currentTry of $maxRetries..."
        
        $success = Invoke-GitCloneWithTimeout -RepoUrl "https://github.com/naibill/Demotool.git" -Directory $repo_dir
        
        if (-not $success) {
            if (Test-Path -Path $repo_dir) {
                Remove-Item -Path $repo_dir -Recurse -Force -ErrorAction SilentlyContinue
                New-Item -Path $repo_dir -ItemType Directory -Force | Out-Null
            }
            
            if ($currentTry -lt $maxRetries) {
                Write-Host "Clone failed, waiting 10 seconds before retry..."
                Start-Sleep -Seconds 10
            }
        }
    }
    
    if (-not $success) {
        Write-Error "Failed to clone repository after $maxRetries attempts"
        exit 1
    }
    
    Write-Host "Repository cloned successfully."
} else {
    Write-Host "Repository already exists in $repo_dir"
}

# Create models directory
$modelsDir = Join-Path -Path $repo_dir -ChildPath "models"
if (-not (Test-Path -Path $modelsDir)) {
    try {
        New-Item -Path $modelsDir -ItemType Directory | Out-Null
        Write-Host "'models' directory created."
    } catch {
        Write-Error "Failed to create models directory: $_"
        exit 1
    }
} else {
    Write-Host "'models' directory already exists."
}

# Environment file handling
$envFile = Join-Path -Path $repo_dir -ChildPath ".env"
if (-not (Test-Path -Path $envFile)) {
    Write-Host "Creating new .env file..."
    do {
        $api_key = Read-Host "Enter API Key"
    } until (Test-ApiKey $api_key)

    # Add URL validation function
    function Test-Url {
        param([string]$url)
        return $url -match '^https?://([\w-]+\.)+[\w-]+(/[\w- ./?%&=]*)?$'
    }

    do {
        $api_url = Read-Host "Enter API URL"
    } until (Test-Url $api_url)

    do {
        $rapid_api_key = Read-Host "Enter Rapid API Key"
    } until (Test-ApiKey $rapid_api_key)

    # Get OpenTelemetry configuration
    do {
        $otel_service_name = Read-Host "Enter the service name for OpenTelemetry monitoring (default: Kodierungstool)"
        if ([string]::IsNullOrWhiteSpace($otel_service_name)) {
            $otel_service_name = "Kodierungstool"
        }
    } until (-not [string]::IsNullOrWhiteSpace($otel_service_name))

    do {
        $otel_endpoint = Read-Host "Enter the OpenTelemetry collector endpoint (default: https://grafana-collector-214718361797.europe-west3.run.app)"
        if ([string]::IsNullOrWhiteSpace($otel_endpoint)) {
            $otel_endpoint = "https://grafana-collector-214718361797.europe-west3.run.app"
        }
    } until (Test-Url $otel_endpoint)

    do {
        $deployment_env = Read-Host "Enter deployment environment (production/development)"
        $deployment_env = $deployment_env.ToLower()
    } until ($deployment_env -eq 'production' -or $deployment_env -eq 'development')

    try {
        @"
DEPLOYMENT_ENV=local
API_KEY=$api_key
API_URL=$api_url
RAPID_API_KEY=$rapid_api_key

# Monitoring
OTEL_SERVICE_NAME="$otel_service_name"
OTEL_EXPORTER_OTLP_ENDPOINT=$otel_endpoint
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_RESOURCE_ATTRIBUTES="deployment.environment=$deployment_env"
"@ | Out-File -FilePath $envFile -Encoding utf8 -ErrorAction Stop
        Write-Host ".env file created successfully."
    } catch {
        Write-Error "Failed to create .env file: $_"
        exit 1
    }
} else {
    Write-Host ".env file already exists, skipping creation."
}

# Deployment choice
do {
    $deploymentChoice = Read-Host "Choose deployment method: Enter '1' for Docker or '2' for Python"
} until ($deploymentChoice -eq '1' -or $deploymentChoice -eq '2')

if ($deploymentChoice -eq '1') {
    # Docker Deployment
    Write-Host "Preparing Docker deployment..."
    
    # Check Docker requirements
    $dockerTools = @{
        'docker' = 'Docker is not installed. Please install from https://docs.docker.com/get-docker/'
        'docker-compose' = 'Docker Compose is not installed. Please install from https://docs.docker.com/compose/install/'
    }
    
    foreach ($tool in $dockerTools.Keys) {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
            Write-Error $dockerTools[$tool]
            exit 1
        }
    }

    # Run Docker setup script
    try {
        Set-Location $repo_dir
        Write-Host "Running Docker setup script..."
        powershell.exe -ExecutionPolicy Bypass -File "scripts/setup_docker.ps1"
    } catch {
        Write-Error "Failed to run Docker setup script: $_"
        exit 1
    }

} elseif ($deploymentChoice -eq '2') {
    # Python Deployment
    Write-Host "Preparing Python deployment..."

    # Check Python 3.12
    $pythonCmd = Get-PythonCommand
    if (-not $pythonCmd) {
        Write-Error "No valid Python 3.12 installation found. Please install Python 3.12 from https://www.python.org/downloads/"
        exit 1
    }

    # Run Python setup script
    try {
        Set-Location $repo_dir
        Write-Host "Running Python setup script..."
        powershell.exe -ExecutionPolicy Bypass -File "scripts/setup_python.ps1"
    } catch {
        Write-Error "Failed to run Python setup script: $_"
        exit 1
    }
}

Write-Host "Setup completed successfully!"