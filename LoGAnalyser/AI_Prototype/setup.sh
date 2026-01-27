#!/bin/bash

echo "=================================="
echo "AI Log Analyzer Prototype Setup"
echo "=================================="
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    deactivate
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Generate synthetic data
echo "Generating synthetic log data..."
python3 data/generate_synthetic_data.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate data"
    exit 1
fi
echo "✓ Data generated"
echo ""

# Train model
echo "Training ML model (this may take 1-2 minutes)..."
python3 models/train_model.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to train model"
    exit 1
fi
echo "✓ Model trained"
echo ""

echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "To run the demo, first activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "Then run:"
echo "  python demo.py"
echo ""
echo "When done, deactivate the environment:"
echo "  deactivate"
echo ""
