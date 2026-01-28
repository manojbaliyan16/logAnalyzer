#!/bin/bash
# Run script for EM_Analyzer on Linux

echo "Starting EM_Analyzer..."
echo "========================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Note: Using system Python. Consider creating venv: python3 -m venv venv"
else
    echo "Error: Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Using Python version: $PYTHON_VERSION"

# Run the analyzer
$PYTHON_CMD EM_Analyzer_main.py

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "========================"
    echo "✓ Job completed successfully"
else
    echo "========================"
    echo "✗ Job failed with exit code: $EXIT_CODE"
    exit $EXIT_CODE
fi
