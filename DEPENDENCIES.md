# Dependency Installation Guide

## All Python Dependencies Discovered

The following dependencies are required for LogAnalyser:

### Core Dependencies
- `jira` - JIRA API integration
- `tabulate` - Table formatting for console output
- `selenium` - Web automation (for dashboard interactions)
- `pandas` - Data processing and analysis
- `openpyxl` - Excel file handling (.xlsx format)
- `xlrd` - Reading old Excel files (.xls format)
- `xlsxwriter` - Writing Excel files
- `requests` - HTTP library
- `datefinder` - Date extraction from text

### Optional Dependencies
- `python-dlt` - For DLT file processing (can use dlt-convert CLI instead)

## Quick Installation

### Method 1: Using Virtual Environment (Recommended)
```bash
cd /home/t0230j7/LogAnalyser/LogAnalyser

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install all dependencies
pip install -r requirements.txt
```

### Method 2: System-wide Installation
```bash
pip install --user -r requirements.txt
```

### Method 3: With break-system-packages (Not Recommended)
```bash
pip install -r requirements.txt --break-system-packages
```

## Verification

Test that all packages are installed:
```bash
source venv/bin/activate
python -c "import jira, tabulate, selenium, pandas, openpyxl, xlrd, xlsxwriter, datefinder; print('All packages installed successfully')"
```

## Current Status

✅ **All Python dependencies are now installed in virtual environment**

The analyzer script (`./run_analyzer.sh`) will:
1. Auto-detect and activate the virtual environment
2. Run with the correct Python interpreter
3. Have access to all required packages

## Next Steps

To run the analyzer:
```bash
./run_analyzer.sh
```

**Note**: The analyzer will require:
- Valid JIRA credentials in `configs/feature_config.json`
- Network access to JIRA server
- At least one ticket to process

## Troubleshooting

If you get "module not found" errors:
1. Ensure virtual environment is activated: `source venv/bin/activate`
2. Reinstall requirements: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.7+)
