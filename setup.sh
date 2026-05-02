#!/bin/bash

# ==================================================================================
# MINIPROJECT 1.0 - SETUP SCRIPT FOR LINUX/MAC
# Microplastics Detection System Setup
# ==================================================================================

set -e  # Exit on any error

echo "================================================================================="
echo "MINIProject 1.0 - Microplastics Detection System Setup"
echo "================================================================================="
echo ""

# Check if Python 3.10+ is installed
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✅ Pip upgraded"

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt
echo "✅ Requirements installed"

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p data/{raw,processed,augmented,train,val,test}
mkdir -p models/{yolo,mobilenet,ensemble,pretrained}
mkdir -p src/{data,models,training,inference,utils}
mkdir -p scripts
mkdir -p notebooks
mkdir -p tests
mkdir -p outputs/{checkpoints,logs,predictions,visualizations}
mkdir -p uploads
echo "✅ Project directories created"

# Create __init__.py files
echo ""
echo "Creating __init__.py files..."
touch src/__init__.py
touch src/data/__init__.py
touch src/models/__init__.py
touch src/training/__init__.py
touch src/inference/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
echo "✅ __init__.py files created"

# Check GPU availability
echo ""
echo "Checking GPU availability..."
python3 -c "
import torch
if torch.cuda.is_available():
    print('✅ GPU available:', torch.cuda.get_device_name(0))
    print('   CUDA version:', torch.version.cuda)
else:
    print('⚠️  No GPU detected, using CPU')
"
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "
try:
    import torch
    import tensorflow as tf
    import cv2
    import ultralytics
    import xgboost
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    print('✅ All core packages imported successfully')
except ImportError as e:
    print('❌ Import error:', e)
    exit(1)
"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << EOF
# ==================================================================================
# MINIPROJECT 1.0 - ENVIRONMENT CONFIGURATION
# ==================================================================================

# ThingSpeak Configuration (Optional)
THINGSPEAK_ENABLED=false
THINGSPEAK_CHANNEL_ID=your_channel_id
THINGSPEAK_WRITE_KEY=your_write_key
THINGSPEAK_READ_KEY=your_read_key

# Model Configuration
YOLOV8_MODEL=yolov8n.pt
YOLOV8_CONFIDENCE_THRESHOLD=0.5
FINAL_CONFIDENCE_THRESHOLD=0.6

# Hardware Configuration
USE_GPU=true
YOLOV8_DEVICE=0

# Data Configuration
DATA_DIR=data
TRAIN_DATA_DIR=\${DATA_DIR}/train
VAL_DATA_DIR=\${DATA_DIR}/val
TEST_DATA_DIR=\${DATA_DIR}/test

# Output Configuration
OUTPUTS_DIR=outputs
RESULTS_DIR=\${OUTPUTS_DIR}/results
VISUALIZATIONS_DIR=\${OUTPUTS_DIR}/visualizations
LOGS_DIR=\${OUTPUTS_DIR}/logs

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=false

# Security Configuration
SECRET_KEY=change-this-in-production
MAX_CONTENT_LENGTH=16777216

# ==================================================================================
EOF
    echo "✅ .env template created"
fi

# Create datasets.yaml for YOLO
echo "Creating datasets.yaml for YOLO..."
cat > data/datasets.yaml << EOF
# ==================================================================================
# YOLO DATASET CONFIGURATION
# ==================================================================================

path: ../data/processed
train: images/train
val: images/val
test: images/test

names:
  0: microplastic
  1: plastic_fragment
  2: plastic_bag
  3: plastic_bottle

# ==================================================================================
EOF
echo "✅ datasets.yaml created"

echo ""
echo "================================================================================="
echo "SETUP COMPLETE! 🎉"
echo "================================================================================="
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your settings"
echo "2. Prepare your dataset in data/train/, data/val/, data/test/"
echo "3. Run: python main.py config"
echo "4. Train models: python main.py train-yolo"
echo "5. Run inference: python main.py predict --source path/to/image.jpg"
echo ""
echo "For web interface:"
echo "1. cd fullstack"
echo "2. pip install -r requirements.txt"
echo "3. python backend/app.py"
echo "4. Open http://localhost:5000"
echo ""
echo "================================================================================="
