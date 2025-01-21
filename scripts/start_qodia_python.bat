@echo off
setlocal EnableDelayedExpansion

echo ===================================
echo Qodia Application Launcher
echo ===================================

:: Check for QODIA_REPO_PATH environment variable
if "%QODIA_REPO_PATH%"=="" (
    echo Error: QODIA_REPO_PATH environment variable not found.
    echo Please run download_and_install.ps1 first.
    exit /b 1
)

:: Change to the repository directory
cd /d "%QODIA_REPO_PATH%" || (
    echo Error: Failed to change to repository directory: %QODIA_REPO_PATH%
    echo Please verify the path exists and you have access to it.
    exit /b 1
)

:: Check if Git is available
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Warning: Git is not installed or not in PATH.
    echo Updates cannot be checked.
    goto :skip_git
)

:: Check if git repository is initialized
if not exist ".git" (
    echo Warning: Git repository not initialized. Skipping updates.
    goto :skip_git
)

echo Checking for updates...

:: Configure repository as safe directory
git config --global --add safe.directory "%QODIA_REPO_PATH%" 2>nul

:: Configure for HTTPS
git config --global url."https://".insteadOf git://
git config --global core.autocrlf true

:: Check remote configuration
git remote -v | findstr "origin.*https://github.com/naibill/Demotool.git" >nul
if %ERRORLEVEL% neq 0 (
    echo Updating remote URL...
    git remote set-url origin "https://github.com/naibill/Demotool.git" >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Warning: Failed to update remote URL. Skipping updates.
        goto :skip_git
    )
)

:: Try to update repository
git remote update origin --prune
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to check for updates. Continuing...
    goto :skip_git
)

:: Check if we're behind the remote
for /f %%i in ('git rev-list HEAD..origin/main --count 2^>nul') do set "updates=%%i"
if %updates% gtr 0 (
    echo Found %updates% update^(s^). Updating...
    
    :: Try normal pull first
    git pull origin main
    if %ERRORLEVEL% neq 0 (
        echo Normal pull failed, attempting force update...
        
        :: Stash any local changes
        git stash -u
        
        :: Fetch and reset to match remote
        git fetch origin main && git reset --hard origin/main
        if %ERRORLEVEL% neq 0 (
            echo Warning: Update failed. Continuing with existing version...
            goto :skip_git
        )
        echo Successfully updated to latest version.
        
        :: Update dependencies after successful pull
        echo Updating dependencies...
        poetry install
        if %ERRORLEVEL% neq 0 (
            echo Error: Failed to update dependencies.
            exit /b 1
        )
    )
) else (
    echo Already up to date.
)

:skip_git

:: Check if Poetry is installed
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Poetry is not installed.
    echo Please run download_and_install.ps1 first.
    exit /b 1
)

:: Check if the virtual environment exists
poetry env info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Poetry virtual environment not found.
    echo Please run setup_python.ps1 first.
    exit /b 1
)

:: Start the application
echo ===================================
echo Starting Qodia-Kodierungstool...
echo ===================================
echo Press Ctrl+C to stop the application
echo.

poetry run python app.py

:: Check exit status
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Application failed to start.
    echo Please check the error messages above.
    pause
    exit /b 1
) else (
    echo.
    echo Application terminated successfully.
    timeout /t 3 >nul
)

endlocal