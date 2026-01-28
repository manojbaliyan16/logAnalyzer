# Quick Start Guide - LogAnalyser Cross-Platform

## 🚀 Fast Setup (5 minutes)

### Step 1: Create Virtual Environment & Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install jira tabulate selenium
```

### Step 2: Install Platform Tools

#### On Linux:
```bash
# For .dlt files
sudo apt-get install dlt-viewer
# OR
pip install python-dlt

# For coredump analysis
sudo apt-get install gdb

# For Selenium
sudo apt-get install firefox-geckodriver
```

#### On Windows:
```powershell
# Download and install:
# - DLT Viewer: https://github.com/GENIVI/dlt-viewer/releases
# - Debugging Tools for Windows (Windows SDK)
# - geckodriver.exe → place in exes/ folder
```

### Step 3: Configure JIRA Credentials
Edit `configs/feature_config.json`:
```json
{
  "Server": "https://your-jira-server.com",
  "user": "your_username",
  "password": "your_password",
  "Maximum Tickets": 1  // Start with 1 for testing
}
```

### Step 4: Run the Analyzer

**Linux**:
```bash
./run_analyzer.sh
```

**Windows**:
```cmd
EM_Analyzer.bat
```

## 📝 What's New?

### Supported Log Types
- ✅ `.dlt` - Automotive diagnostic logs (auto-converted to text)
- ✅ `.txt` - Plain text logs (encoding normalized)
- ✅ `.core`, `.dump`, `.backtrace` - Coredumps (backtrace extracted)
- ✅ `.bin`, `.pro` - Legacy formats (still supported)

### Cross-Platform Support
- Works on both Windows and Linux
- Automatic platform detection
- No code changes needed between platforms

## 🧪 Test Run

### Quick Test with Sample Files
1. Set `"Maximum Tickets": 1` in config
2. Attach test logs to a JIRA ticket
3. Run analyzer
4. Check output:
   ```
   GetLogs/<TicketNo>/
   ├── DLT_LOGS/        # Your converted .dlt files
   ├── TEXT_LOGS/       # Your processed .txt files
   └── COREDUMP_LOGS/   # Your extracted backtraces
   ```

### Verify Results
- Check `Errmem_Dashboard.csv` for ticket status
- Check `Error_log.csv` for any errors
- Verify JIRA ticket updated with:
  - Analysis comments
  - Uploaded processed files
  - Changed labels

## 🔧 Troubleshooting

### "dlt-convert not found"
```bash
# Install DLT tools
sudo apt-get install dlt-viewer
```

### "gdb not found"
```bash
# Install GDB
sudo apt-get install gdb
```

### "Import jira could not be resolved"
```bash
# Install Python packages
pip install jira tabulate selenium
```

### Path errors on Windows
- The code now handles paths automatically
- Ensure you're using the latest updated version

## 📁 Folder Structure After Processing

```
GetLogs/
└── <TicketNo>/
    ├── DLT_LOGS/          # Converted DLT files
    ├── TEXT_LOGS/         # Normalized text logs
    ├── COREDUMP_LOGS/     # Extracted backtraces
    ├── DirectPro_LOGS/    # Direct .pro files
    ├── Decoded_LOGS/      # Decoded .bin files
    └── Downloaded_ZIPS/   # Extracted zips
```

## 📊 Expected Output

### Console
```
Logging into JIRA........
JIRA Connection is successful
Processing DLT files...
✓ Successfully processed DLT file: log.dlt
Processing TXT files...
✓ Successfully processed TXT file: trace.txt
Processing Coredump files...
✓ Successfully processed Coredump: app.core
```

### CSV Files
- `Errmem_Dashboard.csv` - Ticket status
- `Errmem_Metrics.csv` - Processing metrics
- `Error_log.csv` - Any errors encountered

## 🎯 Next Steps

1. **Review Output**: Check processed files in `GetLogs/`
2. **Verify JIRA**: Check ticket comments and labels
3. **Scale Up**: Increase `"Maximum Tickets"` in config
4. **Add Patterns**: Update trace patterns in `configs/Trace_Patterns_config.json`

## 💡 Tips

- Start with 1-2 tickets for initial testing
- Check `Error_log.csv` if something goes wrong
- DLT conversion can be slow for large files (be patient)
- Coredump analysis works best with binary files available

## 📚 Full Documentation

- `README.md` - Complete setup guide
- `MIGRATION_PLAN.md` - Technical implementation details
- `IMPLEMENTATION_SUMMARY.md` - What was changed
- `copilot-instructions.md` - For AI coding assistants

## ⚡ One-Line Installers

### Linux Complete Setup
```bash
pip install jira tabulate selenium python-dlt && sudo apt-get install dlt-viewer gdb firefox-geckodriver -y
```

### Python Only (No System Tools)
```bash
pip install jira tabulate selenium python-dlt
```

## ✅ Success Checklist

- [ ] Python dependencies installed
- [ ] Platform tools installed (dlt-convert, gdb)
- [ ] JIRA credentials configured
- [ ] Test run completed successfully
- [ ] Output files generated
- [ ] JIRA ticket updated correctly

**You're ready to go! 🎉**
