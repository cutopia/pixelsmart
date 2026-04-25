#!/bin/bash

# PixelSmart Startup Script
# This script sets up the virtual environment and launches the application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "PixelSmart Startup Script"
echo "========================="

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Detect GPU support (ROCm vs CUDA)
USE_ROCM=false
if command -v rocm-smi &> /dev/null || [ -d "/opt/rocm" ]; then
    echo "Detected ROCm system - using ROCm requirements"
    USE_ROCM=true
else
    # Check for NVIDIA GPU and nvidia-smi
    if command -v nvidia-smi &> /dev/null; then
        echo "Detected CUDA system - using CUDA requirements"
        USE_ROCM=false
    else
        echo "No GPU detected - using CPU-only requirements"
        USE_ROCM=false
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies based on GPU detection
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Checking/installing dependencies..."
    pip install --upgrade pip > /dev/null 2>&1
    
    if [ "$USE_ROCM" = true ]; then
        echo "Installing ROCm-compatible packages..."
        if [ -f "$SCRIPT_DIR/requirements-rocm.txt" ]; then
            pip install -r "$SCRIPT_DIR/requirements-rocm.txt"
        else
            pip install -r "$SCRIPT_DIR/requirements.txt"
        fi
    else
        echo "Installing standard packages..."
        pip install -r "$SCRIPT_DIR/requirements.txt"
    fi
fi

# Launch the application
echo "Launching PixelSmart..."
python3 "$SCRIPT_DIR/src/pixelsmart/main.py"
