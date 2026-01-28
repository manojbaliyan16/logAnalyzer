# LogAnalyser - Setup Guide

## Recent Updates (January 2026)

The LogAnalyser has been updated to support:
- ✅ **Cross-platform compatibility** (Windows & Linux)
- ✅ **New log file types**: `.dlt`, `.txt`, and coredump/backtrace files
- ✅ **Platform-aware tool selection**

## Prerequisites

### Python Requirements
- Python 3.7 or higher
- Required Python packages (install via `pip install -r requirements.txt`):
  ```
  jira
  tabulate
  selenium
  python-dlt  # Optional, for DLT file processing
  ```

### Platform-Specific Tools

#### Linux
```bash
# Install DLT tools (for .dlt file processing)
sudo apt-get install dlt-viewer
# OR
pip install python-dlt

# Install GDB (for coredump analysis)
sudo apt-get install gdb

# Install Selenium WebDriver
sudo apt-get install firefox-geckodriver
# OR download from: https://github.com/mozilla/geckodriver/releases
```

#### Windows
```powershell
# Install DLT Viewer from: https://github.com/GENIVI/dlt-viewer/releases

# Install Debugging Tools for Windows (for coredump analysis)
# Available as part of Windows SDK

# Download geckodriver.exe for Selenium
# Place in exes/ folder
```

## Installation

### 1. Clone/Extract the Repository
```bash
cd /path/to/LogAnalyser
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install jira tabulate selenium python-dlt
```

### 3. Configure JIRA Credentials
Edit `configs/feature_config.json`:
```json
{
  "Server": "https://your-jira-server.com",
  "user": "your_username",
  "password": "your_password"
}
```

### 4. Place Platform-Specific Executables
- **Windows**: Place `.exe` files in `exes/` folder
  - `Decoder.exe`
  - `ExtractTrcFiles.exe`
  - `geckodriver.exe`
  
- **Linux**: Place binaries in `exes/` folder
  - `decoder` (Linux binary)
  - `extract_trc` (Linux binary)
  - `geckodriver` (Linux binary)

## Running the Analyzer

### On Windows
```cmd
EM_Analyzer.bat
```

Or directly:
```cmd
python EM_Analyzer_main.py
```

### On Linux
```bash
./run_analyzer.sh
```

Or directly:
```bash
python3 EM_Analyzer_main.py
```

## Supported Log File Types

### 1. DLT Files (`.dlt`)
**Diagnostic Log and Trace** - Automotive industry standard
- Automatically converted to text format for analysis
- Requires `dlt-convert` tool or `python-dlt` library
- Processed files saved to: `GetLogs/<TicketNo>/DLT_LOGS/`

### 2. Text Files (`.txt`)
Plain text log files
- Direct processing with encoding normalization
- Supports multiple encodings: UTF-8, Latin-1, ISO-8859-1
- Processed files saved to: `GetLogs/<TicketNo>/TEXT_LOGS/`

### 3. Coredump Files (`.core`, `.dump`, `.dmp`, `.backtrace`)
Crash dump files for debugging
- Requires GDB (Linux) or CDB (Windows)
- Automatically extracts stack traces
- Processed files saved to: `GetLogs/<TicketNo>/COREDUMP_LOGS/`

### 4. Legacy Files (still supported)
- `.bin` - Binary logs (requires TRC files for decoding)
- `.pro` - Processed logs
- `.zip` - Compressed logs (auto-extracted)

## Configuration

### Feature Control (`configs/feature_config.json`)
```json
{
  "SupportedLogTypes": ["bin", "pro", "dlt", "txt", "core", "backtrace", "dump"],
  "DLTConverterPath": "dlt-convert",  # Linux: system path, Windows: full path
  "GDBPath": "gdb",  # Linux: system path, Windows: cdb.exe path
  "DownloadPath": "GetLogs/",
  "Maximum Tickets": 2
}
```

## Folder Structure

After processing, logs are organized as:
```
GetLogs/
└── <TicketNo>/
    ├── Downloaded_ZIPS/     # Extracted zip files
    ├── DirectPro_LOGS/      # Direct .pro files
    ├── Decoded_LOGS/        # Decoded .bin files
    ├── DLT_LOGS/            # Converted .dlt files
    ├── TEXT_LOGS/           # Processed .txt files
    └── COREDUMP_LOGS/       # Extracted backtraces
```

## Troubleshooting

### DLT Files Not Processing
**Error**: `dlt-convert not found`
**Solution**: 
```bash
# Linux
sudo apt-get install dlt-viewer
# OR
pip install python-dlt

# Windows
Download DLT Viewer and add to PATH
```

### Coredump Analysis Fails
**Error**: `GDB not found`
**Solution**:
```bash
# Linux
sudo apt-get install gdb

# Windows
Install Debugging Tools for Windows
```

### Path Errors on Windows
**Issue**: Paths not working
**Solution**: The code now uses `os.path.join()` for cross-platform compatibility. Ensure you're using the latest version.

### Import Errors
**Error**: `Import "jira" could not be resolved`
**Solution**:
```bash
pip install jira tabulate selenium
```

## Development Notes

### Adding New Log Types
1. Update `TicketDir/Ticket.py` - add extension to `valid_extensions`
2. Create handler in `LogsDir/LogTypeHandlers.py`
3. Add processing logic in `LogsDir/Logs.py`
4. Update `configs/feature_config.json`

### Cross-Platform Path Handling
Always use:
```python
import os
path = os.path.join('folder', 'subfolder', 'file.txt')
```

Never use:
```python
path = 'folder\\subfolder\\file.txt'  # Windows-only
path = 'folder/subfolder/file.txt'    # Linux-only (but more portable)
```

## Testing

### Test with Sample Data
1. Set `"Maximum Tickets": 1` in `feature_config.json`
2. Place test log files in a test ticket folder
3. Run the analyzer
4. Check output CSVs:
   - `Errmem_Dashboard.csv`
   - `Errmem_Metrics.csv`
   - `Error_log.csv`

### Verify JIRA Integration
1. Check ticket labels are updated
2. Verify comments are posted
3. Confirm decoded files are uploaded

## Performance Considerations

- **DLT files**: Conversion can be slow for large files (100MB+)
- **Coredump files**: Backtrace extraction depends on file size and binary availability
- **Text files**: Fastest to process, minimal overhead

## Support

For issues or questions:
1. Check `Error_log.csv` for detailed error messages
2. Review console output for processing steps
3. Verify all dependencies are installed
4. Ensure platform-specific tools are in PATH or `exes/` folder

## Migration from Old Version

If migrating from the Windows-only version:
1. Update `configs/feature_config.json` (replace `\\` with `/`)
2. Place Linux binaries in `exes/` folder
3. Install Linux-specific tools (dlt-convert, gdb)
4. Test with a small number of tickets first

## License & Credits

Developed for automotive log analysis in JIRA integration workflows.
