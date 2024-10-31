# PowerShell script for Python deployment setup: installs Poppler, configures Tesseract, and adjusts PATH.

# Step 1: Define the repo directory and Poppler subfolder path
$repo_dir = $env:QODIA_REPO_PATH
$poppler_dir = Join-Path $repo_dir "poppler"

# Step 2: Install Poppler
if (-not (Test-Path -Path $poppler_dir)) {
    Write-Host "Downloading and installing Poppler..."
    $poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
    $poppler_zip = Join-Path $repo_dir "poppler.zip"
    
    # Download Poppler zip file
    Invoke-WebRequest -Uri $poppler_url -OutFile $poppler_zip

    # Extract to poppler_dir
    Expand-Archive -Path $poppler_zip -DestinationPath $poppler_dir -Force
    Remove-Item $poppler_zip

    # Add Poppler bin directory to PATH
    $poppler_bin = Join-Path $poppler_dir "poppler-24.08.0-x86_64" -ChildPath "bin"
    [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $poppler_bin, "Machine")
    Write-Host "Poppler installed and added to PATH."
} else {
    Write-Host "Poppler is already installed."
}

# Step 3: Configure Tesseract
# Check if Tesseract is installed
if (-not (Get-Command tesseract -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Tesseract is not installed. Please install it first from https://ub-mannheim.github.io/Tesseract_Dokumentation/Tesseract_Doku_Windows.html."
    exit 1
}

# Find Tesseract data directory and download German language file
$tessdata_dir = (tesseract --print-parameters | Select-String -Pattern "TESSDATA_PREFIX").Matches.Groups[1].Value

if (-not (Test-Path -Path (Join-Path $tessdata_dir "deu.traineddata"))) {
    Write-Host "Downloading German language file for Tesseract..."
    $deu_data_url = "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata"
    Invoke-WebRequest -Uri $deu_data_url -OutFile (Join-Path $tessdata_dir "deu.traineddata")
    Write-Host "German language file downloaded and configured for Tesseract."
} else {
    Write-Host "Tesseract German language file already exists."
}

# Step 4: Navigate to the repository directory and install Poetry environment
Set-Location $repo_dir
Write-Host "Initializing the Poetry environment..."
poetry install
Write-Host "Poetry environment set up successfully."