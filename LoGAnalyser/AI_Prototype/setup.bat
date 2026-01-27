@echo off
echo ==================================
echo AI Log Analyzer Prototype Setup
echo ==================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Found %PYTHON_VERSION%
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Generate synthetic data
echo Generating synthetic log data...
python data\generate_synthetic_data.py
if errorlevel 1 (
    echo ❌ Failed to generate data
    pause
    exit /b 1
)
echo ✓ Data generated
echo.

REM Train model
echo Training ML model (this may take 1-2 minutes)...
python models\train_model.py
if errorlevel 1 (
    echo ❌ Failed to train model
    pause
    exit /b 1
)
echo ✓ Model trained
echo.

echo ==================================
echo ✓ Setup Complete!
echo ==================================
echo.
echo To run the demo:
echo   python demo.py
echo.
pause
