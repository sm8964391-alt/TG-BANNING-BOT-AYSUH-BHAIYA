#!/bin/bash

echo "==================================="
echo "Telegram Super-Manager Setup Script"
echo "==================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH!"
    echo "Please install Python 3.7 or higher and try again."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "Setting up virtual environment..."

# Check if venv exists, if not create it
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created virtual environment."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Run the setup script
echo "Running setup script..."
python setup.py

echo ""
echo "==================================="
echo "Setup complete!"
echo ""
echo "To test your installation: python test_setup.py"
echo "To start the application: python frontend/main.py"
echo "==================================="

# Make the script executable
chmod +x setup.py
if [ -f "test_setup.py" ]; then
    chmod +x test_setup.py
fi