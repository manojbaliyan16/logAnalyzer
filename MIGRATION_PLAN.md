# Migration Plan: Cross-Platform & New Log Types Support

## Overview
Adapting LogAnalyser for Linux/Windows compatibility and adding support for .dlt, .txt, and coredump/backtrace files.

## Phase 1: Cross-Platform Path Handling

### Files to Update
1. **configSettings.py** - Fix hardcoded paths
2. **All modules** that construct file paths

### Implementation Strategy
```python
# Before (Windows-only)
path = 'configs\\feature_config.json'
folder = base_path + ticket_number + "\\"

# After (Cross-platform)
import os
from pathlib import Path

path = os.path.join('configs', 'feature_config.json')
# OR
path = Path('configs') / 'feature_config.json'

folder = os.path.join(base_path, ticket_number)
```

### Key Changes Needed
- [ ] `configSettings.py`: Update all `open()` calls with path separators
- [ ] `LogsDir/Logs.py`: Fix folder creation paths
- [ ] `TicketDir/Manipulate_TicketData.py`: Update TRC paths
- [ ] `DB_Interface/JIRA_InitFetchUpdate.py`: Fix download paths
- [ ] Search codebase for `\\` and replace with `os.path.join()` or `Path()`

## Phase 2: Platform-Specific Tool Selection

### Create Platform Abstraction Layer
Create new file: `Utils/platform_tools.py`

```python
import platform
import os
from pathlib import Path

class PlatformTools:
    def __init__(self):
        self.os_type = platform.system()  # 'Windows', 'Linux', 'Darwin'
    
    def get_decoder_path(self):
        if self.os_type == 'Windows':
            return os.path.join('exes', 'Decoder.exe')
        elif self.os_type == 'Linux':
            return os.path.join('exes', 'decoder')  # Linux binary
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
    
    def get_trc_extractor_path(self):
        if self.os_type == 'Windows':
            return os.path.join('exes', 'ExtractTrcFiles.exe')
        elif self.os_type == 'Linux':
            return os.path.join('exes', 'extract_trc')
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
```

### Update Logs.py
Replace direct exe calls with platform-aware calls:
```python
from Utils.platform_tools import PlatformTools

platform_tools = PlatformTools()
decoder_path = platform_tools.get_decoder_path()
```

## Phase 3: New Log File Type Support

### 3.1 Add File Type Detection

Update `TicketDir/Ticket.py` - `validateTicketAttachments()`:
```python
def validateTicketAttachments(self, attachmentsPathList):
    status = "INVALID"
    valid_extensions = [".bin", ".pro", ".txt", ".exv", ".zip", 
                       ".dlt", ".core", ".backtrace", ".dump"]
    
    for path in attachmentsPathList:
        if any(path.endswith(ext) for ext in valid_extensions):
            status = "VALID"
            break
        # Handle downloadPipe special case
        if "downloadPipe" in path:
            status = "VALID"
            break
    return status
```

### 3.2 Create Log Type Handlers

Create new file: `LogsDir/LogTypeHandlers.py`

```python
import os
import subprocess
from pathlib import Path

class DLTLogHandler:
    """Handler for .dlt (Diagnostic Log and Trace) files"""
    
    def __init__(self, dlt_file_path):
        self.dlt_file = dlt_file_path
    
    def convert_to_text(self, output_path):
        """Convert .dlt to readable text format"""
        # Option 1: Use dlt-convert command line tool
        # Option 2: Use python-dlt library
        try:
            # Using dlt-convert (needs to be installed)
            cmd = ['dlt-convert', '-a', self.dlt_file, '-o', output_path]
            subprocess.run(cmd, check=True)
            return output_path
        except:
            # Fallback: Use python-dlt library
            import dlt  # pip install python-dlt
            # Implementation here
            pass
    
    def extract_traces(self):
        """Extract trace patterns from DLT file"""
        text_log = self.convert_to_text(self.dlt_file + '.txt')
        return text_log


class TextLogHandler:
    """Handler for plain .txt log files"""
    
    def __init__(self, txt_file_path):
        self.txt_file = txt_file_path
    
    def validate_format(self):
        """Check if text log is in expected format"""
        # Check for timestamps, proper structure
        return True
    
    def extract_traces(self):
        """Text files can be processed directly"""
        return self.txt_file


class CoredumpHandler:
    """Handler for coredump and backtrace files"""
    
    def __init__(self, core_file_path, binary_path=None):
        self.core_file = core_file_path
        self.binary_path = binary_path
    
    def extract_backtrace(self, output_path):
        """Extract backtrace from coredump using gdb"""
        if platform.system() == 'Linux':
            # Use gdb to extract backtrace
            gdb_cmd = f"gdb -batch -ex 'bt' {self.binary_path} {self.core_file}"
            result = subprocess.run(gdb_cmd, shell=True, 
                                   capture_output=True, text=True)
            
            with open(output_path, 'w') as f:
                f.write(result.stdout)
            return output_path
        elif platform.system() == 'Windows':
            # Use WinDbg or other Windows debugger
            # Implementation for Windows
            pass
    
    def analyze_crash(self):
        """Analyze crash signature and stack trace"""
        backtrace_file = self.extract_backtrace(self.core_file + '.bt.txt')
        return backtrace_file
```

### 3.3 Update LogsDir/Logs.py

Add new log type handling in `getLogs()`:
```python
def getLogs(self):
    # Existing code...
    attacheddltList = []
    attachedtxtList = []
    attachedcoredumpList = []
    
    for attachment in attachmentPaths:
        attachment = str(attachment)
        if attachment.endswith(".pro"):
            attachedproList.append(attachment)
        elif attachment.endswith(".bin"):
            attachedbinList.append(attachment)
        elif attachment.endswith(".zip"):
            attachedziplist.append(attachment)
        elif attachment.endswith(".dlt"):
            attacheddltList.append(attachment)
        elif attachment.endswith(".txt"):
            attachedtxtList.append(attachment)
        elif attachment.endswith((".core", ".dump", ".backtrace")):
            attachedcoredumpList.append(attachment)
        elif "downloadPipe" in attachment:
            attachedList.append(attachment)
    
    # Process DLT files
    if attacheddltList:
        processed_dlt = self.processDLTFiles(attacheddltList)
        renamed_validatedProList.extend(processed_dlt)
    
    # Process TXT files
    if attachedtxtList:
        processed_txt = self.processTextFiles(attachedtxtList)
        renamed_validatedProList.extend(processed_txt)
    
    # Process Coredump files
    if attachedcoredumpList:
        processed_coredumps = self.processCoredumps(attachedcoredumpList)
        renamed_validatedProList.extend(processed_coredumps)
    
    # Return updated LogList
    return LogList

def processDLTFiles(self, dlt_files):
    """Process .dlt files and convert to analyzable format"""
    from LogsDir.LogTypeHandlers import DLTLogHandler
    
    processed_files = []
    for dlt_file in dlt_files:
        handler = DLTLogHandler(dlt_file)
        text_log = handler.extract_traces()
        processed_files.append(text_log)
    return processed_files

def processTextFiles(self, txt_files):
    """Process .txt log files"""
    from LogsDir.LogTypeHandlers import TextLogHandler
    
    processed_files = []
    for txt_file in txt_files:
        handler = TextLogHandler(txt_file)
        if handler.validate_format():
            processed_files.append(txt_file)
    return processed_files

def processCoredumps(self, coredump_files):
    """Process coredump files"""
    from LogsDir.LogTypeHandlers import CoredumpHandler
    
    processed_files = []
    for core_file in coredump_files:
        handler = CoredumpHandler(core_file)
        backtrace = handler.analyze_crash()
        processed_files.append(backtrace)
    return processed_files
```

### 3.4 Update Pattern Matching

Update `PatternMatchingDir/PatternMatching.py` to handle new formats:
```python
def getLogHandler(log):
    """Open log file with appropriate handler based on type"""
    if log.endswith('.dlt.txt') or log.endswith('.bt.txt'):
        # These are converted files
        pass
    
    # Existing encoding fallback logic
    attachmentHandler = "Invalid File"
    try:
        attachmentHandler = open(log, encoding="utf8", errors='ignore')
    except:
        try:
            attachmentHandler = open(log, encoding="latin-1", errors='ignore')
        except:
            attachmentHandler = open(log, encoding="ISO-8859-1", errors='ignore')
    return attachmentHandler
```

## Phase 4: Configuration Updates

### Update configs/feature_config.json
Add new configuration options:
```json
{
  "FeatureControl": [{
    "SupportedLogTypes": ["bin", "pro", "dlt", "txt", "core", "backtrace"],
    "DLTConverterPath": "exes/dlt-convert",
    "GDBPath": "/usr/bin/gdb",
    "Platform": "auto"
  }]
}
```

## Phase 5: Testing Strategy

### Create Test Data Structure
```
test_data/
├── sample_logs/
│   ├── test.dlt
│   ├── test.txt
│   ├── test.core
│   ├── test.bin
│   └── test.pro
└── expected_outputs/
    ├── test.dlt.expected.txt
    └── test.core.expected.bt
```

### Unit Tests to Create
1. `tests/test_platform_tools.py` - Test platform detection
2. `tests/test_log_handlers.py` - Test each log type handler
3. `tests/test_path_handling.py` - Verify cross-platform paths
4. `tests/test_end_to_end.py` - Full pipeline test

## Implementation Checklist

### Cross-Platform Support
- [ ] Create `Utils/platform_tools.py`
- [ ] Update `configSettings.py` path handling
- [ ] Update `LogsDir/Logs.py` path construction
- [ ] Update `TicketDir/Manipulate_TicketData.py`
- [ ] Update `DB_Interface/JIRA_InitFetchUpdate.py`
- [ ] Search and replace all `\\` hardcoded paths
- [ ] Update `EM_Analyzer.bat` → create `run_analyzer.sh` for Linux

### New Log Type Support
- [ ] Create `LogsDir/LogTypeHandlers.py`
- [ ] Update `TicketDir/Ticket.py` validation
- [ ] Update `LogsDir/Logs.py` with new handlers
- [ ] Update `configs/feature_config.json`
- [ ] Install required tools (dlt-convert, gdb)
- [ ] Add pattern configs for new log types

### Dependencies to Install
```bash
# Linux
pip install python-dlt
apt-get install dlt-viewer  # or equivalent
apt-get install gdb

# Python packages
pip install pathlib  # if Python < 3.4
```

## Priority Order
1. **HIGH**: Cross-platform path handling (breaks on Linux currently)
2. **HIGH**: Platform tool abstraction
3. **MEDIUM**: .txt file support (simplest to implement)
4. **MEDIUM**: .dlt file support (requires external tools)
5. **LOW**: Coredump support (most complex, may need binary analysis)

## Notes
- Test on both Windows and Linux after each phase
- Keep backward compatibility with existing .bin and .pro files
- Document new dependencies in README
- Consider Docker containerization for consistent environments
