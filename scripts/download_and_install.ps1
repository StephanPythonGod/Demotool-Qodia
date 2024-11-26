# PowerShell script to set up Qodia-Kodierungstool with persistent environment variable and interactive deployment choice

# Function to check if running as administrator
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent();
    $principal = New-Object Security.Principal.WindowsPrincipal $user
    return $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

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

# Function to add directory to PATH if it's not already included
function Add-ToPath {
    param(
        [string]$PathToAdd
    )
    if (Test-Path -Path $PathToAdd) {
        $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        if ($currentPath -notlike "*$PathToAdd*") {
            $newPath = "$currentPath;$PathToAdd"
            [System.Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
            Write-Host "Added $PathToAdd to system PATH."
            return $true
        }
    }
    return $false
}

# Check for administrator rights
if (-not (Test-Administrator)) {
    Write-Error "This script requires administrator rights. Please run PowerShell as administrator."
    exit 1
}

# Set PowerShell Execution Policy for the current session if needed
try {
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process -Force
} catch {
    Write-Error "Failed to set execution policy: $_"
    exit 1
}

# Verify required tools based on deployment choice
Write-Host "Checking system requirements..."
$commonTools = @{
    'git' = 'Git is not installed. Please install from https://git-scm.com/downloads'
}

# Step 1: Define and check the repository directory environment variable
$repoEnvVar = "QODIA_REPO_PATH"

# Check if environment variable exists at machine level
$machineEnvPath = [System.Environment]::GetEnvironmentVariable($repoEnvVar, "Machine")
if ([string]::IsNullOrWhiteSpace($machineEnvPath)) {
    do {
        $repo_dir = Read-Host "Enter the directory where you want to clone the repository"
    } until (Test-ValidPath $repo_dir)
    
    try {
        [System.Environment]::SetEnvironmentVariable($repoEnvVar, $repo_dir, "Machine")
        # Update current session's environment variable
        $env:QODIA_REPO_PATH = $repo_dir
        Write-Host "Repository path saved to environment variable $repoEnvVar."
    } catch {
        Write-Error "Failed to set environment variable: $_"
        exit 1
    }
} else {
    $repo_dir = $machineEnvPath
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

# Clone repository with proper error handling
if (-not (Test-Path -Path (Join-Path $repo_dir ".git"))) {
    # Check if directory is empty
    $items = Get-ChildItem -Path $repo_dir -Force
    if ($items.Count -gt 0) {
        Write-Error "Directory is not empty. Please choose an empty directory for the repository."
        exit 1
    }
    
    try {
        Write-Host "Cloning repository to $repo_dir..."
        git clone "https://github.com/naibill/Qodia-Kodierungstool.git" $repo_dir
        
        # Verify the clone was successful by checking for .git directory
        if (-not (Test-Path -Path (Join-Path $repo_dir ".git"))) {
            throw "Git clone appeared to succeed but .git directory not found"
        }
        Write-Host "Repository cloned successfully."
    } catch {
        Write-Error "Failed to clone repository: $_"
        exit 1
    }
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

# Environment file handling - simplified to skip if exists
$envFile = Join-Path -Path $repo_dir -ChildPath ".env"
if (-not (Test-Path -Path $envFile)) {
    Write-Host "Creating new .env file..."
    do {
        $api_key = Read-Host "Enter API Key"
    } until (Test-ApiKey $api_key)

    do {
        $api_url = Read-Host "Enter API URL"
    } until ($api_url -match '^https?://.+')

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
    } until ($otel_endpoint -match '^https?://.+')

    do {
        $deployment_env = Read-Host "Enter deployment environment (production/development)"
        $deployment_env = $deployment_env.ToLower()
    } until ($deployment_env -eq 'production' -or $deployment_env -eq 'development')

    # Create .env file with error handling
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

    # Start Docker service with proper error handling
    try {
        $service = Get-Service docker -ErrorAction Stop
        if ($service.Status -ne 'Running') {
            Write-Host "Starting Docker service..."
            Start-Service docker
            $timeout = 30
            $timer = [Diagnostics.Stopwatch]::StartNew()
            while ($service.Status -ne 'Running' -and $timer.Elapsed.TotalSeconds -lt $timeout) {
                Start-Sleep -Seconds 1
                $service.Refresh()
            }
            if ($service.Status -ne 'Running') {
                throw "Docker service failed to start within $timeout seconds"
            }
            Write-Host "Docker service started successfully."
        } else {
            Write-Host "Docker service is already running."
        }
    } catch {
        Write-Error "Docker service error: $_"
        exit 1
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

    # Check Python 3.12 and add default paths
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Python is not installed. Please install Python 3.12 from https://www.python.org/downloads/"
        
        # Add default Python installation paths to PATH
        $pythonPaths = @(
            "${env:ProgramFiles}\Python312",
            "${env:ProgramFiles}\Python312\Scripts",
            "${env:ProgramFiles(x86)}\Python312",
            "${env:ProgramFiles(x86)}\Python312\Scripts",
            "${env:LocalAppData}\Programs\Python\Python312",
            "${env:LocalAppData}\Programs\Python\Python312\Scripts"
        )
        
        foreach ($path in $pythonPaths) {
            Add-ToPath $path
        }
        
        Write-Host "Default Python paths have been added to system PATH."
        Write-Host "After installing Python, please restart your PowerShell session and run this script again."
        exit 1
    } else {
        try {
            $pythonVersion = (python --version 2>&1).ToString()
            if ($pythonVersion -match 'Python 3\.12\.\d+') {
                Write-Host "Python 3.12 is installed: $pythonVersion"
            } else {
                Write-Error "Wrong Python version installed: $pythonVersion. Please install Python 3.12 from https://www.python.org/downloads/"
                exit 1
            }
        } catch {
            Write-Error "Failed to check Python version. Please install Python 3.12 from https://www.python.org/downloads/"
            exit 1
        }
    }

    # Check and install Poetry
    if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Host "Poetry is not installed. Installing Poetry..."
        try {
            (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
            
            # Add Poetry to PATH
            $python_scripts = [System.IO.Path]::Combine($env:APPDATA, "Python\Scripts")
            Add-ToPath $python_scripts
            
            # Verify Poetry installation
            if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
                throw "Poetry installation failed"
            }
            Write-Host "Poetry installed successfully."
        } catch {
            Write-Error "Failed to install Poetry: $_"
            Write-Host "Please install Poetry manually from https://python-poetry.org/docs/#installation"
            exit 1
        }
    } else {
        Write-Host "Poetry is already installed."
    }

    # Check Tesseract and add default paths
    if (-not (Get-Command tesseract -ErrorAction SilentlyContinue)) {
        Write-Host "Tesseract is not installed. Please install it from https://digi.bib.uni-mannheim.de/tesseract/"
        
        # Add default Tesseract installation paths to PATH
        $tesseractPaths = @(
            "${env:ProgramFiles}\Tesseract-OCR",
            "${env:ProgramFiles(x86)}\Tesseract-OCR",
            "${env:LocalAppData}\Programs\Tesseract-OCR"
        )
        
        foreach ($path in $tesseractPaths) {
            Add-ToPath $path
        }
        
        Write-Host "Default Tesseract paths have been added to system PATH."
        Write-Host "After installing Tesseract, please restart your PowerShell session and run this script again."
        exit 1
    } else {
        Write-Host "Tesseract is installed."
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