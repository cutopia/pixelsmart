#!/bin/bash

# Run PixelSmart tests

# Activate virtual environment if available
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install test dependencies if needed
pip install pytest --quiet 2>/dev/null || true

# Run tests with verbose output
pytest tests/ -v "$@"
