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

# Enhanced Function to add directory to PATH if it's not already included
function Add-ToPath {
    param(
        [string]$PathToAdd
    )
    
    if (-not (Test-Path -Path $PathToAdd)) {
        Write-Host "Path does not exist: $PathToAdd"
        return $false
    }

    # Get both Machine and User PATH
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")

    # Split paths into arrays for better comparison
    $machinePathArray = $machinePath -split ";"
    $userPathArray = $userPath -split ";"

    # Check if path already exists in either Machine or User PATH
    if (($machinePathArray -contains $PathToAdd) -or ($userPathArray -contains $PathToAdd)) {
        Write-Host "Path already exists in environment: $PathToAdd"
        return $true
    }

    try {
        # Add to Machine PATH
        $newMachinePath = ($machinePathArray + $PathToAdd) -join ";"
        [System.Environment]::SetEnvironmentVariable("Path", $newMachinePath, "Machine")
        
        # Update current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        Write-Host "Successfully added to system PATH: $PathToAdd"
        
        # Broadcast WM_SETTINGCHANGE message to notify other applications of the environment change
        if (-not ("Win32.NativeMethods" -as [Type])) {
            Add-Type -Namespace Win32 -Name NativeMethods -MemberDefinition @"
                [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
                public static extern IntPtr SendMessageTimeout(
                    IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam,
                    uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
"@
        }
        
        $HWND_BROADCAST = [IntPtr]0xffff
        $WM_SETTINGCHANGE = 0x1a
        $result = [UIntPtr]::Zero
        
        [Win32.NativeMethods]::SendMessageTimeout(
            $HWND_BROADCAST,
            $WM_SETTINGCHANGE,
            [UIntPtr]::Zero,
            "Environment",
            2,
            5000,
            [ref]$result
        ) | Out-Null

        return $true
    }
    catch {
        Write-Error "Failed to add to PATH: $_"
        return $false
    }
}

# Function to verify PATH updates
function Test-PathEntry {
    param(
        [string]$PathToTest
    )
    
    $currentPath = $env:Path -split ";"
    if ($currentPath -contains $PathToTest) {
        Write-Host "Verified: $PathToTest is in current session PATH"
        return $true
    }
    Write-Host "Warning: $PathToTest is not in current session PATH"
    return $false
}

# Function to get Python command
function Get-PythonCommand {
    # First try the 'py' launcher as it's more reliable on Windows
    if (Get-Command py -ErrorAction SilentlyContinue) {
        # Verify py command works and points to Python 3.12
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
    
    # Then try the 'python' command
    if (Get-Command python -ErrorAction SilentlyContinue) {
        try {
            $pythonVersion = (& python --version 2>&1).ToString()
            # Check if it's not the Microsoft Store redirect
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
    $pythonCmd = Get-PythonCommand
    if (-not $pythonCmd) {
        Write-Host "No valid Python 3.12 installation found. Please install Python 3.12 from https://www.python.org/downloads/"
        
        # Add default Python installation paths to PATH
        $pythonPaths = @(
            "${env:ProgramFiles}\Python312",
            "${env:ProgramFiles}\Python312\Scripts",
            "${env:ProgramFiles(x86)}\Python312",
            "${env:ProgramFiles(x86)}\Python312\Scripts",
            "${env:LocalAppData}\Programs\Python\Python312",
            "${env:LocalAppData}\Programs\Python\Python312\Scripts"
        )
        
        $pathsAdded = $false
        foreach ($path in $pythonPaths) {
            if (Test-Path $path) {
                if (Add-ToPath $path) {
                    $pathsAdded = $true
                    Test-PathEntry $path
                }
            }
        }
        
        if ($pathsAdded) {
            Write-Host "Python paths have been added to system PATH. Please restart your PowerShell session."
            Write-Host "After installing Python, please restart your PowerShell session and run this script again."
        } else {
            Write-Host "No valid Python paths found to add to PATH."
        }
        exit 1
    } else {
        try {
            # No need to check version again since we already did in Get-PythonCommand
            Write-Host "Using Python command: $pythonCmd"
        } catch {
            Write-Error "Failed to verify Python version. Please install Python 3.12 from https://www.python.org/downloads/"
            exit 1
        }
    }

    # Check and install Poetry
    if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Host "Poetry is not installed. Installing Poetry..."
        try {
            # Create a temporary file for the installation script
            $tempFile = [System.IO.Path]::GetTempFileName()
            $installScript = (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content
            Set-Content -Path $tempFile -Value $installScript -Encoding UTF8

            # Run the installation script with the detected Python command
            if ($pythonCmd -eq "py -3.12") {
                & py -3.12 $tempFile
            } else {
                & $pythonCmd $tempFile
            }

            # Clean up the temporary file
            Remove-Item -Path $tempFile -Force
            
            # Add Poetry to PATH with verification
            $poetryPath = [System.IO.Path]::Combine($env:APPDATA, "Python", "Scripts")
            if (Add-ToPath $poetryPath) {
                Test-PathEntry $poetryPath
                
                # Refresh environment variables in current session
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
                
                if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
                    throw "Poetry installation succeeded but command is not available. Please restart PowerShell."
                }
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
    function Test-TesseractInstallation {
        try {
            $tesseractVersion = & tesseract --version 2>&1
            if ($tesseractVersion -match "tesseract") {
                Write-Host "Tesseract is installed and working."
                return $true
            }
        } catch {
            return $false
        }
        return $false
    }

    if (-not (Test-TesseractInstallation)) {
        Write-Host "Tesseract is not installed or not working properly. Please install it from https://digi.bib.uni-mannheim.de/tesseract/"
        
        # Add default Tesseract installation paths to PATH
        $tesseractPaths = @(
            "${env:ProgramFiles}\Tesseract-OCR",
            "${env:ProgramFiles(x86)}\Tesseract-OCR",
            "${env:LocalAppData}\Programs\Tesseract-OCR"
        )
        
        $pathsAdded = $false
        foreach ($path in $tesseractPaths) {
            if (Test-Path $path) {
                if (Add-ToPath $path) {
                    $pathsAdded = $true
                    Test-PathEntry $path
                }
            }
        }
        
        if ($pathsAdded) {
            Write-Host "Tesseract paths have been added to system PATH."
            # Check again after adding paths
            if (Test-TesseractInstallation) {
                Write-Host "Tesseract is now properly configured."
            } else {
                Write-Host "Please restart your PowerShell session and run this script again."
                exit 1
            }
        } else {
            Write-Host "Please install Tesseract and run this script again."
            exit 1
        }
    } else {
        Write-Host "Tesseract is installed and working properly."
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