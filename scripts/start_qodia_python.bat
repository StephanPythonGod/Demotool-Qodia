@echo off
REM Qodia Launch Script

REM Check for QODIA_REPO_PATH environment variable
IF "%QODIA_REPO_PATH%"=="" (
    echo Error: The environment variable QODIA_REPO_PATH is not set.
    echo Please run the installation script to configure the environment.
    pause
    exit /b
)

REM Navigate to the repository directory
cd /d "%QODIA_REPO_PATH%"

REM Check if Poetry is available
where poetry >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Poetry is not installed or not available in the PATH.
    echo Please ensure Poetry is installed and added to your PATH.
    pause
    exit /b
)

REM Run the Qodia application using Poetry and Streamlit
echo Starting Qodia application...
poetry run streamlit run app.py

REM Pause at the end in case of errors
echo Application terminated. Press any key to exit.
pause