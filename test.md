# LogAnalyser Copilot Instructions

## Project Overview
LogAnalyser is an **automated JIRA ticket analysis tool** for automotive error memory logs. It connects to JIRA, fetches field claim tickets, downloads/decodes log files (`.bin`, `.pro`, `.zip`), analyzes them using pattern matching, and posts results back to JIRA.

## Architecture & Data Flow

### Pipeline Stages (EM_Analyzer_main.py)
1. **Config Loading** (`configSettings.py`) → Load all JSON configs from `configs/`
2. **DB Fetch** (`DB_Interface/`) → JIRA connection, query tickets, download attachments
3. **Ticket Factory** (`TicketFactoryDir/`) → Iterate through fetched tickets
4. **Validation** (`TicketDir/Ticket.py`) → Check required fields (SW_ID, Relevance, Brand, attachments)
5. **Manipulation** → Extract buildVersion, customerVersion, platform, variant, faultDate
6. **Log Processing** (`LogsDir/Logs.py`) → Extract zips, decode `.bin` files using external decoders
7. **Analysis** (`AnalyzerDir/Analyzer.py`) → Pattern matching against trace configs
8. **JIRA Update** → Post analysis comments, upload decoded files, update labels
9. **Dashboard** (`Dashboard_UpdaterDir/`) → Write CSV metrics

### Data Structures
- **FTMDT** (Fetched Ticket Metadata Table): `[TicketNo, SW_ID, Relevance, Brand, AttachmentList, Description, TicketFolderPath, TicketReference, Components]`
- **MTMD** (Manipulated Ticket Metadata): `[status, tkt_number, SW_ID, customerVersion, buildVersion, platform, Relevance, variant, attachmentList, faultDate, TRCPath, Components]`
- **PTMD** (Processed Ticket Metadata): `[TicketNo, ticket_reference, label_to_change, logList, analysis_results, result_comment, default_assignee]`

## Critical Conventions

### Path Handling
- All paths use **Windows-style backslashes** (`\\`) in code
- Config paths: `configs\\feature_config.json` (hardcoded)
- Download base path: `GetLogs\\` (from feature_config.json)
- Ticket structure: `GetLogs\\<TicketNo>\\Downloaded_ZIPS\\`, `\\DirectPro_LOGS`, `\\Decoded_LOGS`

### File Type Handling
- `.pro` files: Direct processable logs
- `.bin` files: Require decoding with TRC files using `exes\\Decoder.exe`
- `.zip` files: Extracted to `Downloaded_ZIPS\\` subfolder
- `downloadPipe` attachments: Special handling for SW_SWUPDATE component

### Pattern Matching
- **Trace patterns** (`configs/Trace_Patterns_config.json`): Search for error signatures with occurrence counts
- **Validation patterns**: Extract SW_ID from logs using regex
- Each pattern has COMPONENT_RESP field for recommended component analysis
- Patterns support text string and regex searches

### Global Configuration
- `Global/global_var.py`: Holds shared config dictionaries loaded at startup
- Access via `Global.global_var.g_feature_control_config`, `g_trace_pattern_config`, etc.
- NEVER modify globals mid-execution (read-only after init)

## Key Workflows

### Running the Analyzer
```bash
# Main entry point (run from project root)
python EM_Analyzer_main.py

# Or via batch file   
EM_Analyzer.bat
```

### Adding New Trace Patterns
Edit `configs/Trace_Patterns_config.json`:
```json
{
  "PATTERN": "exact string or regex to match",
  "OCCURRENCE_COUNT": 1,
  "OCCURRENCE_CONTINUITY": "Not Continuous",
  "TRACE_COMMENT": "Human-readable explanation",
  "COMPONENT_RESP": "SW_COMPONENT_NAME"
}
```

### JIRA Integration
- Credentials in `configs/feature_config.json` (Server, user, password)
- Certificate required: `DB_Interface/Certification/hi-cmtsappsintranetboschcom.crt`
- Label workflow: `EMA_Trial` → `EM_Analyzer_PreAnalyzed_auto` or `EM_Analyzer_Failed` or `EM_Analyzer_need_info`

## External Dependencies
- **jira library**: JIRA API access (`from jira import JIRA`)
- **External EXEs** (in `exes/`): `Decoder.exe`, `ExtractTrcFiles.exe`, `geckodriver.exe`
- **Selenium/geckodriver**: Used for dashboard interactions (Firefox)

## Error Handling Pattern
- All ticket processing wrapped in try-except in main loop
- Errors logged to `ERROR_LOGS` list → written to `Error_log.csv` via `BuildLogCreatorDir/BuildLogCreator.py`
- Failed tickets get label `EM_Analyzer_Failed`, comment with traceback

## Testing Approach
- No formal test suite exists
- Test by setting `"Maximum Tickets": 1-2` in `configs/feature_config.json`
- Check output CSVs: `Errmem_Dashboard.csv`, `Errmem_Metrics.csv`, `Error_log.csv`
- Verify JIRA ticket updates manually

## Common Pitfalls
- **Hardcoded Windows paths**: Code assumes Windows environment (backslashes, `.bat` file)
- **External exe dependency**: Decoder.exe must be in `exes/` for bin decoding
- **JIRA credentials**: Must update `feature_config.json` with valid credentials before running
- **TRC availability**: If TRCs unavailable/empty, bin files cannot be decoded (generates "Could not process" message)
- **Log encoding**: Files opened with multiple encoding fallbacks (`utf8` → `latin-1` → `ISO-8859-1`)
