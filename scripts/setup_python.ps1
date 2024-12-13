# PowerShell script for Python deployment setup: installs Poppler, configures Tesseract, and adjusts PATH.

# Step 1: Define the repo directory and Poppler subfolder path
$repo_dir = $env:QODIA_REPO_PATH
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

        # Add Poppler bin directory to PATH
        $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        if ($currentPath -notlike "*$poppler_bin*") {
            [System.Environment]::SetEnvironmentVariable("Path", $currentPath + ";" + $poppler_bin, "Machine")
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
            Write-Host "Poppler added to PATH."
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
        Write-Error "Existing Poppler installation appears to be corrupt. Could not find poppler version directory. Please delete the poppler directory and run the script again."
        exit 1
    }
    
    $poppler_bin = Join-Path $version_dir.FullName "Library\bin"
    $pdfinfo_path = Join-Path $poppler_bin "pdfinfo.exe"
    
    if (-not (Test-Path -Path $pdfinfo_path)) {
        Write-Error "Existing Poppler installation appears to be corrupt. Please delete the poppler directory and run the script again."
        exit 1
    }
    
    # Ensure it's in PATH
    $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$poppler_bin*") {
        [System.Environment]::SetEnvironmentVariable("Path", $currentPath + ";" + $poppler_bin, "Machine")
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        Write-Host "Poppler added to PATH."
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
    
    # Try to get Tesseract installation path from where the executable is
    $tesseract_exe = (Get-Command tesseract).Source
    $tesseract_dir = Split-Path $tesseract_exe -Parent
    $tessdata_dir = Join-Path (Split-Path $tesseract_dir -Parent) "tessdata"
    
    if (-not (Test-Path -Path $tessdata_dir)) {
        # Alternative locations to check
        $possible_locations = @(
            "C:\Program Files\Tesseract-OCR\tessdata",
            "C:\Program Files (x86)\Tesseract-OCR\tessdata",
            "${env:ProgramFiles}\Tesseract-OCR\tessdata",
            "${env:ProgramFiles(x86)}\Tesseract-OCR\tessdata"
        )
        
        foreach ($loc in $possible_locations) {
            if (Test-Path -Path $loc) {
                $tessdata_dir = $loc
                break
            }
        }
    }
    
    if (-not (Test-Path -Path $tessdata_dir)) {
        throw "Could not find Tesseract data directory"
    }
    
    Write-Host "Found Tesseract data directory: $tessdata_dir"
    
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

# Step 4: Navigate to the repository directory and install Poetry environment
try {
    Set-Location $repo_dir
    Write-Host "Initializing the Poetry environment..."
    poetry install
    if ($LASTEXITCODE -ne 0) {
        throw "Poetry install failed with exit code $LASTEXITCODE"
    }
    Write-Host "Poetry environment set up successfully."
}
catch {
    Write-Error "Failed to set up Poetry environment: $_"
    exit 1
}