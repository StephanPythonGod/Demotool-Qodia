@echo off
setlocal enabledelayedexpansion

echo ===================================
echo Qodia Application Launcher
echo ===================================

REM Check for QODIA_REPO_PATH environment variable
IF "%QODIA_REPO_PATH%"=="" (
    echo [ERROR] The environment variable QODIA_REPO_PATH is not set.
    echo Please run the installation script to configure the environment.
    pause
    exit /b 1
)

REM Navigate to the repository directory
cd /d "%QODIA_REPO_PATH%" 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to navigate to %QODIA_REPO_PATH%
    echo Please verify the directory exists and you have access to it.
    pause
    exit /b 1
)

REM Check if Git is available
where git >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Git is not installed or not in PATH.
    echo Updates cannot be checked.
    goto :skip_git
)

REM Configure safe directory
echo Configuring repository as safe directory...
git config --global --add safe.directory "%QODIA_REPO_PATH%" 2>nul

REM Check for Git updates
echo Checking for updates...
git remote update origin --prune

REM Check if we're behind the remote
for /f "tokens=*" %%a in ('git rev-list HEAD...origin/main --count 2^>nul') do set updates=%%a
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to check for updates.
    goto :skip_git
)

if %updates% GTR 0 (
    echo Updates available. Attempting to update...
    
    REM Check for local changes
    git diff --quiet
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Local changes detected. Cannot update automatically.
        choice /C YN /M "Do you want to continue without updating"
        IF !ERRORLEVEL! EQU 2 exit /b 1
        goto :skip_git
    )
    
    REM Try to pull updates
    git pull origin main
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Failed to pull updates.
        choice /C YN /M "Do you want to continue without updating"
        IF !ERRORLEVEL! EQU 2 exit /b 1
    ) else (
        echo Successfully updated to the latest version.
        
        REM Update dependencies after pull
        echo Updating dependencies...
        poetry install
        if %ERRORLEVEL% NEQ 0 (
            echo [WARNING] Failed to update dependencies.
            choice /C YN /M "Do you want to continue anyway"
            IF !ERRORLEVEL! EQU 2 exit /b 1
        )
    )
) else (
    echo No updates available.
)

:skip_git

REM Check if Poetry is available
where poetry >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Poetry is not installed or not in PATH.
    echo Please ensure Poetry is installed and added to your PATH.
    pause
    exit /b 1
)

REM Check if the virtual environment exists and create if needed
poetry env info -p >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Setting up virtual environment...
    poetry install
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to set up virtual environment.
        pause
        exit /b 1
    )
)

REM Check if app.py exists
IF NOT EXIST "app.py" (
    echo [ERROR] app.py not found in %QODIA_REPO_PATH%
    echo Please verify the repository is properly set up.
    pause
    exit /b 1
)

echo ===================================
echo Starting Qodia application...
echo ===================================
echo Press Ctrl+C to stop the application
echo.

REM Run the Qodia application using Poetry and Streamlit
poetry run streamlit run app.py

REM Check if the application terminated with an error
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application terminated with an error.
    pause
) else (
    echo.
    echo Application terminated successfully.
    timeout /t 3 >nul
)