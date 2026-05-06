@echo off
echo ===================================
echo Telegram Super-Manager Setup Script
echo ===================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher and try again.
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Setting up virtual environment...

:: Check if venv exists, if not create it
if not exist .venv (
    python -m venv .venv
    echo Created virtual environment.
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Run the setup script
echo Running setup script...
python setup.py

echo.
echo ===================================
echo Setup complete!
echo.
echo To test your installation: python test_setup.py
echo To start the application: python frontend/main.py
echo ===================================

pause