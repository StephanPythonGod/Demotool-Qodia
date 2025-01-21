# PowerShell script for Python deployment setup: installs Poppler, configures Tesseract, and adjusts PATH.

# Function to add directory to PATH (User scope)
function Add-ToUserPath {
    param(
        [string]$PathToAdd
    )
    
    if (-not (Test-Path -Path $PathToAdd)) {
        Write-Host "Path does not exist: $PathToAdd"
        return $false
    }

    # Get User PATH
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $userPathArray = $userPath -split ";"

    # Check if path already exists
    if ($userPathArray -contains $PathToAdd) {
        Write-Host "Path already exists in environment: $PathToAdd"
        return $true
    }

    try {
        # Add to User PATH
        $newUserPath = ($userPathArray + $PathToAdd) -join ";"
        [System.Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
        
        # Update current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + 
                    [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        Write-Host "Successfully added to user PATH: $PathToAdd"
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

# Get repository directory from environment variable
$repo_dir = [System.Environment]::GetEnvironmentVariable("QODIA_REPO_PATH", "User")
if (-not $repo_dir) {
    Write-Error "QODIA_REPO_PATH environment variable not found. Please run download_and_install.ps1 first."
    exit 1
}

# Step 1: Define the Poppler subfolder path
$poppler_dir = Join-Path $repo_dir "poppler"

# Step 2: Install Poppler
if (-not (Test-Path -Path $poppler_dir)) {
    Write-Host "Downloading and installing Poppler..."
    $poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
    $poppler_zip = Join-Path $repo_dir "poppler.zip"
    
    try {
        # Create directory if it doesn't exist
        if (-not (Test-Path -Path $poppler_dir)) {
            New-Item -Path $poppler_dir -ItemType Directory -Force | Out-Null
        }

        # Download Poppler zip file with progress bar
        Write-Host "Downloading Poppler..."
        $ProgressPreference = 'Continue'
        Invoke-WebRequest -Uri $poppler_url -OutFile $poppler_zip
        
        if (-not (Test-Path -Path $poppler_zip)) {
            throw "Download failed: Zip file not found"
        }

        # Extract to poppler_dir
        Write-Host "Extracting Poppler..."
        Expand-Archive -Path $poppler_zip -DestinationPath $poppler_dir -Force
        
        # Find the version-specific directory
        $version_dir = Get-ChildItem -Path $poppler_dir -Directory | Where-Object { $_.Name -like "poppler-*" } | Select-Object -First 1
        if (-not $version_dir) {
            throw "Extraction failed: Could not find poppler version directory"
        }
        
        # Verify extraction with corrected path
        $poppler_bin = Join-Path $version_dir.FullName "Library\bin"
        if (-not (Test-Path -Path $poppler_bin)) {
            throw "Extraction failed: Binary directory not found in $poppler_bin"
        }

        # Clean up zip file
        Remove-Item $poppler_zip -ErrorAction SilentlyContinue

        # Add Poppler bin directory to PATH (User scope)
        if (-not (Add-ToUserPath $poppler_bin)) {
            throw "Failed to add Poppler to PATH"
        }

        # Verify installation by checking for a specific executable
        $pdfinfo_path = Join-Path $poppler_bin "pdfinfo.exe"
        if (-not (Test-Path -Path $pdfinfo_path)) {
            throw "Installation verification failed: pdfinfo.exe not found"
        }

        Write-Host "Poppler installed successfully."
    }
    catch {
        Write-Error "Failed to install Poppler: $_"
        # Cleanup on failure
        if (Test-Path -Path $poppler_zip) {
            Remove-Item $poppler_zip -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -Path $poppler_dir) {
            Remove-Item $poppler_dir -Recurse -Force -ErrorAction SilentlyContinue
        }
        exit 1
    }
} else {
    Write-Host "Poppler directory already exists. Verifying installation..."
    
    # Find the version-specific directory in existing installation
    $version_dir = Get-ChildItem -Path $poppler_dir -Directory | Where-Object { $_.Name -like "poppler-*" } | Select-Object -First 1
    if (-not $version_dir) {
        Write-Error "Existing Poppler installation appears to be corrupt. Could not find poppler version directory."
        exit 1
    }
    
    $poppler_bin = Join-Path $version_dir.FullName "Library\bin"
    $pdfinfo_path = Join-Path $poppler_bin "pdfinfo.exe"
    
    if (-not (Test-Path -Path $pdfinfo_path)) {
        Write-Error "Existing Poppler installation appears to be corrupt. Please delete the poppler directory and run the script again."
        exit 1
    }
    
    # Ensure it's in PATH
    if (-not (Add-ToUserPath $poppler_bin)) {
        Write-Error "Failed to add existing Poppler installation to PATH"
        exit 1
    }
    
    Write-Host "Existing Poppler installation verified."
}

# Update the Tesseract check section
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

# Step 3: Configure Tesseract
Write-Host "Checking Tesseract installation..."
if (-not (Test-TesseractInstallation)) {
    Write-Error "Error: Tesseract is not installed or not working properly. Please install it from https://ub-mannheim.github.io/Tesseract_Dokumentation/Tesseract_Doku_Windows.html"
    exit 1
}

# Find Tesseract data directory
try {
    Write-Host "Locating Tesseract data directory..."
    
    # Common Tesseract installation paths
    $possible_locations = @(
        "${env:ProgramFiles}\Tesseract-OCR\tessdata",
        "${env:ProgramFiles(x86)}\Tesseract-OCR\tessdata",
        "${env:LOCALAPPDATA}\Programs\Tesseract-OCR\tessdata",
        "${env:USERPROFILE}\AppData\Local\Programs\Tesseract-OCR\tessdata",
        "${env:USERPROFILE}\Tesseract-OCR\tessdata"
    )

    # Try to get Tesseract installation path from where the executable is
    try {
        $tesseract_exe = (Get-Command tesseract -ErrorAction Stop).Source
        $tesseract_dir = Split-Path $tesseract_exe -Parent
        $tessdata_dir = Join-Path (Split-Path $tesseract_dir -Parent) "tessdata"
        if (Test-Path -Path $tessdata_dir) {
            $possible_locations = @($tessdata_dir) + $possible_locations
        }
    } catch {
        Write-Host "Could not determine Tesseract path from executable, checking common locations..."
    }
    
    $tessdata_dir = $null
    foreach ($loc in $possible_locations) {
        Write-Host "Checking location: $loc"
        if (Test-Path -Path $loc) {
            $tessdata_dir = $loc
            Write-Host "Found Tesseract data directory: $tessdata_dir"
            break
        }
    }
    
    if (-not $tessdata_dir) {
        throw "Could not find Tesseract data directory in any of the expected locations. Please verify your Tesseract installation."
    }
    
    # Download German language file if needed
    $deu_traineddata = Join-Path $tessdata_dir "deu.traineddata"
    if (-not (Test-Path -Path $deu_traineddata)) {
        Write-Host "Downloading German language file for Tesseract..."
        $deu_data_url = "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata"
        
        try {
            Invoke-WebRequest -Uri $deu_data_url -OutFile $deu_traineddata
            if (-not (Test-Path -Path $deu_traineddata)) {
                throw "Download failed: Language file not found"
            }
            Write-Host "German language file downloaded and configured for Tesseract."
        }
        catch {
            Write-Error "Failed to download German language file: $_"
            exit 1
        }
    } else {
        Write-Host "Tesseract German language file already exists."
    }
}
catch {
    Write-Error "Failed to configure Tesseract: $_"
    exit 1
}

# Step 4: Install Poetry environment
try {
    Set-Location $repo_dir
    Write-Host "Initializing the Poetry environment..."
    
    # Verify Poetry installation
    if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Error "Poetry is not installed. Please run download_and_install.ps1 first."
        exit 1
    }
    
    # Install dependencies
    Write-Host "Installing project dependencies..."
    $result = poetry install 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Poetry install failed with output: $result"
    }
    Write-Host "Poetry environment set up successfully."
}
catch {
    Write-Error "Failed to set up Poetry environment: $_"
    exit 1
}

Write-Host "Python setup completed successfully!"