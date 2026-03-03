#!/usr/bin/env bash
# STEM WEEK User App - macOS/Linux Launcher

echo
echo ========================================
echo STEM WEEK User App Launcher
echo ========================================
echo

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from python.org or your package manager"
    exit 1
fi

PYTHON=python3

# create venv if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv || {
        echo "Failed to create venv. Make sure the 'python3-venv' package is installed.";
        exit 1;
    }
fi

# prefer to use venv executables directly, activation optional
VENV_PY=".venv/bin/python"
VENV_PIP=".venv/bin/pip"
if [ ! -x "$VENV_PY" ]; then
    echo "Virtual environment python executable missing. Please recreate venv."
    exit 1
fi

# install requirements via venv pip
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }

# set interpreter for launch
PYTHON="$VENV_PY"


# Launch
python main.py
