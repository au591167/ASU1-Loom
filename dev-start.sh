#!/bin/bash
# ASU1-Loom Development Launcher (Linux/Mac)
# Quick start script for Unix-based systems

echo ""
echo "========================================"
echo "  ASU1-Loom Development Launcher"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

echo "Starting ASU1-Loom..."
echo ""

# Run the Python launcher
python3 dev-launcher.py

# Exit code
exit $?
