@echo off
REM ==================================================================================
REM MINIPROJECT 1.0 - SETUP SCRIPT FOR WINDOWS
REM Microplastics Detection System Setup
REM ==================================================================================

echo ==================================================================================
echo MINIProject 1.0 - Microplastics Detection System Setup
echo ==================================================================================
echo.

REM Check if Python is installed
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)
echo ✅ Pip upgraded

REM Install requirements
echo.
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)
echo ✅ Requirements installed

REM Create necessary directories
echo.
echo Creating project directories...
if not exist "data" mkdir data
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
if not exist "data\augmented" mkdir data\augmented
if not exist "data\train" mkdir data\train
if not exist "data\val" mkdir data\val
if not exist "data\test" mkdir data\test

if not exist "models" mkdir models
if not exist "models\yolo" mkdir models\yolo
if not exist "models\mobilenet" mkdir models\mobilenet
if not exist "models\ensemble" mkdir models\ensemble
if not exist "models\pretrained" mkdir models\pretrained

if not exist "src" mkdir src
if not exist "src\data" mkdir src\data
if not exist "src\models" mkdir src\models
if not exist "src\training" mkdir src\training
if not exist "src\inference" mkdir src\inference
if not exist "src\utils" mkdir src\utils

if not exist "scripts" mkdir scripts
if not exist "notebooks" mkdir notebooks
if not exist "tests" mkdir tests

if not exist "outputs" mkdir outputs
if not exist "outputs\checkpoints" mkdir outputs\checkpoints
if not exist "outputs\logs" mkdir outputs\logs
if not exist "outputs\predictions" mkdir outputs\predictions
if not exist "outputs\visualizations" mkdir outputs\visualizations

if not exist "uploads" mkdir uploads
echo ✅ Project directories created

REM Create __init__.py files
echo.
echo Creating __init__.py files...
echo. > src\__init__.py
echo. > src\data\__init__.py
echo. > src\models\__init__.py
echo. > src\training\__init__.py
echo. > src\inference\__init__.py
echo. > src\utils\__init__.py
echo. > tests\__init__.py
echo ✅ __init__.py files created

REM Check GPU availability
echo.
echo Checking GPU availability...
python -c "import torch; print('✅ GPU available:', torch.cuda.get_device_name(0)) if torch.cuda.is_available() else print('⚠️  No GPU detected, using CPU')"
echo.

REM Verify installation
echo Verifying installation...
python -c "
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
if errorlevel 1 (
    echo ❌ Verification failed
    pause
    exit /b 1
)
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env template...
    (
        echo # ==================================================================================
        echo # MINIPROJECT 1.0 - ENVIRONMENT CONFIGURATION
        echo # ==================================================================================
        echo.
        echo # ThingSpeak Configuration ^(Optional^)
        echo THINGSPEAK_ENABLED=false
        echo THINGSPEAK_CHANNEL_ID=your_channel_id
        echo THINGSPEAK_WRITE_KEY=your_write_key
        echo THINGSPEAK_READ_KEY=your_read_key
        echo.
        echo # Model Configuration
        echo YOLOV8_MODEL=yolov8n.pt
        echo YOLOV8_CONFIDENCE_THRESHOLD=0.5
        echo FINAL_CONFIDENCE_THRESHOLD=0.6
        echo.
        echo # Hardware Configuration
        echo USE_GPU=true
        echo YOLOV8_DEVICE=0
        echo.
        echo # Data Configuration
        echo DATA_DIR=data
        echo TRAIN_DATA_DIR=%%DATA_DIR%%/train
        echo VAL_DATA_DIR=%%DATA_DIR%%/val
        echo TEST_DATA_DIR=%%DATA_DIR%%/test
        echo.
        echo # Output Configuration
        echo OUTPUTS_DIR=outputs
        echo RESULTS_DIR=%%OUTPUTS_DIR%%/results
        echo VISUALIZATIONS_DIR=%%OUTPUTS_DIR%%/visualizations
        echo LOGS_DIR=%%OUTPUTS_DIR%%/logs
        echo.
        echo # API Configuration
        echo API_HOST=0.0.0.0
        echo API_PORT=5000
        echo API_DEBUG=false
        echo.
        echo # Security Configuration
        echo SECRET_KEY=change-this-in-production
        echo MAX_CONTENT_LENGTH=16777216
        echo.
        echo # ==================================================================================
    ) > .env
    echo ✅ .env template created
)

REM Create datasets.yaml for YOLO
echo Creating datasets.yaml for YOLO...
(
    echo # ==================================================================================
    echo # YOLO DATASET CONFIGURATION
    echo # ==================================================================================
    echo.
    echo path: ../data/processed
    echo train: images/train
    echo val: images/val
    echo test: images/test
    echo.
    echo names:
    echo   0: microplastic
    echo   1: plastic_fragment
    echo   2: plastic_bag
    echo   3: plastic_bottle
    echo.
    echo # ==================================================================================
) > data\datasets.yaml
echo ✅ datasets.yaml created

echo.
echo ==================================================================================
echo SETUP COMPLETE! 🎉
echo ==================================================================================
echo.
echo Next steps:
echo 1. Edit config.yaml with your settings
echo 2. Prepare your dataset in data\train\, data\val\, data\test\
echo 3. Run: python main.py config
echo 4. Train models: python main.py train-yolo
echo 5. Run inference: python main.py predict --source path\to\image.jpg
echo.
echo For web interface:
echo 1. cd fullstack
echo 2. pip install -r requirements.txt
echo 3. python backend\app.py
echo 4. Open http://localhost:5000
echo.
echo ==================================================================================
pause
