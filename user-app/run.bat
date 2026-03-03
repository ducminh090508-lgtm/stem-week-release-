@echo off
REM STEM WEEK User App - Windows Batch Runner

echo.
echo ========================================
echo STEM WEEK User App Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import textual" >nul 2>&1
if errorlevel 1 (
    echo Running initial setup...
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Run the app
python main.py
pause
