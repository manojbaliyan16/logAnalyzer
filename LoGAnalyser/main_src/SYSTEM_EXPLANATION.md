# LoGAnalyser - Automated Error Memory Log Analysis System

## Overview
This is an **automated JIRA ticket processing system** that analyzes automotive Error Memory (EM) logs from field complaints. It fetches tickets from JIRA, downloads and validates log files, performs pattern-based analysis, and updates tickets with automated diagnostic results.

## System Architecture

### Main Components

1. **EM_Analyzer_main.py** - Main orchestrator
2. **configSettings.py** - Configuration loader (JSON configs)
3. **DB_Interface/** - JIRA connection and operations
4. **TicketFactory/** - Factory pattern for ticket creation
5. **TicketDir/** - Ticket validation and data manipulation
6. **LogsDir/** - Log file processing (download, decode, validate)
7. **AnalyzerDir/** - Pattern matching and analysis engine
8. **PatternMatchingDir/** - Trace and comment pattern matching
9. **Dashboard_UpdaterDir/** - CSV dashboard generation
10. **BuildLogCreator/** - Error logging

---

## Detailed Workflow Explanation

### Phase 1: Configuration & Initialization
```
1. Load JSON configurations:
   - feature_config.json → Feature control (JIRA settings, labels, components)
   - Validation_Patterns_config.json → Log validation patterns
   - Trace_Patterns_config.json → Error trace patterns to search
   - downloadPipe_Patterns_config.json → Download pipe patterns
   - Comment_Patterns_config.json → Comment templates

2. Store configs in global variables (Global/global_var.py)
```

### Phase 2: JIRA Ticket Fetching
```
1. DBInterfacing class connects to JIRA server
2. Generates JQL query based on:
   - Project name
   - Labels (e.g., "EM_Analyzer_pending")
   - Components (e.g., "SW_SWUPDATE")
3. Fetches ticket metadata (FTMDT):
   - Ticket number
   - SW_ID (software version)
   - Relevance (vehicle platform)
   - Brand
   - Attachments (.pro, .bin, .zip files)
   - Description (contains fault date)
   - Component
```

### Phase 3: Ticket Processing Loop (For Each Ticket)

#### 3.1 Ticket Validation
```
Ticket.ValidateTicketData() checks:
- Are attachments present?
- Are attachments valid format (.bin, .pro, .zip, downloadPipe)?
- Is Relevance field filled?
- Is Brand field filled?

IF INVALID → Mark ticket for "EM_Analyzer_need_info" label
```

#### 3.2 Ticket Data Manipulation
```
Ticket.ManipulateTicketData():
- Extract buildVersion from SW_ID
- Get customerVersion from dashboard lookup
- Extract platform (gen3/gen4) from Relevance
- Extract variant (AIVI2, PIVI2, etc.)
- Parse fault occurrence date from description (dd.mm.yy format)
- Determine TRC (Trace Class) path for decoding
```

#### 3.3 Log File Processing
```
Logs.getLogs():
a) Categorize attachments:
   - Direct .pro files (protocol files)
   - .bin files (binary logs - need decoding)
   - .zip files (extract and categorize contents)
   - downloadPipe files

b) Validate Direct .pro files:
   - Check if SW_ID in file matches JIRA SW_ID
   - Rename validated files with "_directPro.pro" suffix
   - Move to DirectPro_LOGS folder

c) Decode .bin files (if TRCs available):
   - Change extension .bin → .pro
   - Decode using TRC files (trace class definitions)
   - Validate decoded files
   - Rename with "_decoded_auto.pro" suffix
   - Move to Decoded_LOGS folder

d) Handle .zip files:
   - Extract to Downloaded_ZIPS folder
   - Recursively process .pro/.bin files inside
   - Rename with zip name prefix

RESULT: logList = [validLogList, invalidLogList, downloadPipeList]
```

#### 3.4 Log Analysis
```
Analyzer.analyzeLogs():

For each VALID log file:

a) Comment Pattern Matching (Pre-Analysis):
   - Extract log name
   - Extract actual SW_ID from traces
   - Get customer version
   - Extract log collection date
   - Determine log availability date range
   - Check if logs available during fault occurrence date
   - If logs missing/overwritten:
     * Get overwritten blocks info
     * Get missing blocks info
     * Extract serial number
     * Extract part number
   - Generate Hansy tool link (for visualization)

b) Trace Pattern Matching (Main Analysis):
   IF fault date available OR component is "SW_SWUPDATE":
   - Search for configured trace patterns in log
   - Match against Trace_Patterns_config.json
   - Extract:
     * Matched pattern descriptions
     * Line numbers
     * Occurrence dates
     * Recommended components to analyze

c) Frame Log Result:
   - Combine comment parameters
   - Add trace pattern matches
   - Generate structured comment for JIRA

For each INVALID log:
- Generate error message explaining validation failure

RESULT: logsAnalysisResultsList (one analysis per log)
```

### Phase 4: JIRA Update
```
For each processed ticket:
1. Add comments with analysis results
2. Upload decoded log files as attachments (not original .pro files)
3. Update ticket label:
   - "EM_Analyzer_PreAnalyzed_auto" (success)
   - "EM_Analyzer_need_info" (validation failed)
   - "EM_Analyzer_Failed" (processing error)
4. Assign ticket to default assignee
```

### Phase 5: Dashboard & Metrics
```
Dashboard_Updater:
- Errmem_Dashboard.csv:
  * Ticket number
  * Ticket status (label)
  * ARTA comment
  * Assignee

- Errmem_Metrics.csv:
  * PROCESSED_TICKET_COUNT
  * SUCCEEEDED_TICKET_COUNT
  * FAILED_TICKET_COUNT
```

### Phase 6: Error Logging
```
BuildLogCreator:
- If any errors occurred, write to Error_log.csv:
  * Ticket number
  * Error traceback
  * Error type (Processing Error, Result Update Error, etc.)
```

---

## Sequence Diagram

\`\`\`
┌─────────────┐       ┌──────────────┐      ┌─────────────┐      ┌────────────┐      ┌──────────┐      ┌──────────┐      ┌─────────────┐
│EM_Analyzer_ │       │configSettings│      │DBInterfacing│      │TicketFactory│      │  Ticket  │      │   Logs   │      │  Analyzer   │
│   main.py   │       │              │      │   (JIRA)    │      │             │      │          │      │          │      │             │
└──────┬──────┘       └──────┬───────┘      └──────┬──────┘      └─────┬──────┘      └────┬─────┘      └────┬─────┘      └──────┬──────┘
       │                     │                     │                     │                   │                 │                   │
       │ 1. Load Configs     │                     │                     │                   │                 │                   │
       ├────────────────────>│                     │                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 2. Return Config Data│                    │                     │                   │                 │                   │
       │<────────────────────┤                     │                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 3. Initialize DB Connection               │                     │                   │                 │                   │
       ├──────────────────────────────────────────>│                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 4. Generate JQL Query                     │                     │                   │                 │                   │
       ├──────────────────────────────────────────>│                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 5. Fetch Tickets (FTMDT)                  │                     │                   │                 │                   │
       ├──────────────────────────────────────────>│                     │                   │                 │                   │
       │                     │                  [Downloads attachments]   │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 6. Return FTMDT (List of Ticket Metadata)│                     │                   │                 │                   │
       │<──────────────────────────────────────────┤                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 7. Create TicketFactory(FTMDT)            │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────>│                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ ══════════════════════════════════ FOR EACH TICKET ═══════════════════════════════════════════════════════════════════  │
       │                     │                     │                     │                   │                 │                   │
       │ 8. Pick Ticket(index)                     │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────>│                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 9. Return FTMD (Single Ticket Metadata)   │                     │                   │                 │                   │
       │<───────────────────────────────────────────────────────────────┤                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 10. Create Ticket(FTMD)                   │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────>│                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 11. ValidateTicketData()                  │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────>│                 │                   │
       │                     │                     │                     │              [Check attachments,    │                   │
       │                     │                     │                     │               Relevance, Brand]     │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 12. Return VTMD (Validation Result: VALID/INVALID + reasons)   │                   │                 │                   │
       │<───────────────────────────────────────────────────────────────────────────────────┤                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ [IF INVALID: Add to INVTMDT, set label "need_info", continue]  │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 13. ManipulateTicketData(VTMD)            │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────>│                 │                   │
       │                     │                     │                     │         [Extract buildVersion,      │                   │
       │                     │                     │                     │          customerVersion, platform,  │                   │
       │                     │                     │                     │          variant, faultDate, TRCs]   │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 14. Return MTMD (Manipulated Ticket Metadata)                  │                   │                 │                   │
       │<───────────────────────────────────────────────────────────────────────────────────┤                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 15. Create Logs(MTMD)                     │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────────────────────>│                   │
       │                     │                     │                     │                   │                 │                   │
       │ 16. getLogs()                             │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────────────────────>│                   │
       │                     │                     │                     │                   │    [Categorize attachments:        │
       │                     │                     │                     │                   │     .pro, .bin, .zip]              │
       │                     │                     │                     │                   │    [Extract zip files]             │
       │                     │                     │                     │                   │    [Validate .pro files]           │
       │                     │                     │                     │                   │    [Decode .bin files using TRCs]  │
       │                     │                     │                     │                   │    [Rename & organize files]       │
       │                     │                     │                     │                   │                 │                   │
       │ 17. Return logList [validLogs, invalidLogs, downloadPipeFiles] │                   │                 │                   │
       │<───────────────────────────────────────────────────────────────────────────────────────────────────┤                   │
       │                     │                     │                     │                   │                 │                   │
       │ 18. Create Analyzer(logList, faultDate, buildVer, custVer, component)              │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────>│
       │                     │                     │                     │                   │                 │                   │
       │ 19. analyzeLogs()                         │                     │                   │                 │                   │
       ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────>│
       │                     │                     │                     │                   │                 │  [FOR EACH VALID LOG:
       │                     │                     │                     │                   │                 │   - Get comment patterns
       │                     │                     │                     │                   │                 │     (log dates, SW_ID,
       │                     │                     │                     │                   │                 │      missing blocks, etc)
       │                     │                     │                     │                   │                 │   - Match trace patterns
       │                     │                     │                     │                   │                 │     (error signatures)
       │                     │                     │                     │                   │                 │   - Frame result comment]
       │                     │                     │                     │                   │                 │                   │
       │ 20. Return analysis_results (list of formatted comments)        │                   │                 │                   │
       │<───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
       │                     │                     │                     │                   │                 │                   │
       │ 21. Prepare PTMD (Processed Ticket Metadata)                    │                   │                 │                   │
       │     [TicketNo, reference, label, logList, analysis_results, status, assignee]      │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ ══════════════════════════════════ END FOR EACH TICKET ════════════════════════════════════════════════════════════════ │
       │                     │                     │                     │                   │                 │                   │
       │ 22. Update JIRA Tickets                   │                     │                   │                 │                   │
       ├──────────────────────────────────────────>│                     │                   │                 │                   │
       │                     │       [FOR EACH PROCESSED TICKET:         │                   │                 │                   │
       │                     │        - Add comments with analysis]      │                   │                 │                   │
       │                     │        - Upload decoded log attachments]  │                   │                 │                   │
       │                     │        - Update label (PreAnalyzed_auto)] │                   │                 │                   │
       │                     │        - Assign to default assignee]      │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 23. Update Complete                       │                     │                   │                 │                   │
       │<──────────────────────────────────────────┤                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 24. Create Dashboard                      │                     │                   │                 │                   │
       │     [Errmem_Dashboard.csv & Errmem_Metrics.csv]                 │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
       │ 25. Write Error Logs (if any)             │                     │                   │                 │                   │
       │     [Error_log.csv]                       │                     │                   │                 │                   │
       │                     │                     │                     │                   │                 │                   │
\`\`\`

---

## Key Design Patterns Used

### 1. **Factory Pattern**
- **TicketFactory**: Creates ticket objects from metadata
- Decouples ticket creation from processing logic

### 2. **Strategy Pattern (Implicit)**
- Different analysis strategies for different log types
- Pattern matching strategies (text patterns vs regex patterns)

### 3. **Template Method Pattern**
- Log analysis follows a template:
  1. Validate
  2. Decode (if needed)
  3. Extract metadata
  4. Pattern match
  5. Generate result

### 4. **Façade Pattern**
- **DBInterfacing**: Simplifies complex JIRA API operations
- **Logs**: Hides complexity of file handling, decoding, validation

### 5. **Data Transfer Object (DTO)**
- FTMDT (Fetched Ticket Metadata Table)
- VTMD (Validated Ticket Metadata)
- MTMD (Manipulated Ticket Metadata)
- PTMDT (Processed Ticket Metadata Table)

---

## Data Flow Summary

\`\`\`
JIRA Tickets
    ↓
FTMDT (Raw ticket data)
    ↓
Ticket Validation → VTMD
    ↓
Data Manipulation → MTMD (enriched with versions, dates, platform)
    ↓
Log Download & Decode → logList (valid/invalid logs)
    ↓
Pattern Analysis → analysis_results (diagnostic comments)
    ↓
PTMDT (processed tickets with results)
    ↓
JIRA Update (comments, attachments, labels)
    ↓
Dashboard CSV (metrics & status)
\`\`\`

---

## Important Files & Their Purpose

| File/Folder | Purpose |
|-------------|---------|
| **EM_Analyzer_main.py** | Main orchestrator - controls entire workflow |
| **configSettings.py** | Loads JSON configs into global variables |
| **configs/*.json** | Configuration files for patterns, features, validation |
| **DB_Interface/** | JIRA connection, query generation, fetch, update |
| **TicketFactory/** | Factory to create ticket objects |
| **TicketDir/Ticket.py** | Validates and manipulates ticket data |
| **TicketDir/Manipulate_TicketData.py** | Helper functions (version extraction, date parsing) |
| **LogsDir/Logs.py** | Downloads, decodes, validates, organizes log files |
| **AnalyzerDir/Analyzer.py** | Main analysis engine - pattern matching orchestrator |
| **PatternMatchingDir/** | Pattern matching implementations (trace patterns, comments) |
| **Dashboard_UpdaterDir/** | Generates CSV dashboards for metrics |
| **BuildLogCreatorDir/** | Creates error logs for failed processing |
| **GetLogs/NCG3D-XXXXX/** | Downloaded ticket folders with logs |
| **Errmem_Dashboard.csv** | Output dashboard with ticket status |
| **Errmem_Metrics.csv** | Processing metrics (success/fail counts) |

---

## Typical Use Case Example

**Scenario**: Field complaint about vehicle infotainment crash

1. **Input**: JIRA ticket NCG3D-306058
   - SW_ID: AIVI_SW5244
   - Relevance: Nissan AIVI2-S1
   - Attachment: EM_TRACE.pro (error memory log)
   - Description: "Crash on 2024/03/15"

2. **Processing**:
   - Validates SW_ID field is present ✓
   - Validates attachment exists ✓
   - Extracts fault date: 15.03.24
   - Gets customer version: SW5244 → P1234
   - Platform: gen4, Variant: AIVI2
   - Validates .pro file has matching SW_ID
   - Analyzes patterns in log:
     * Finds "TARGET_OFF" pattern at line 1234
     * Finds "WATCHDOG_RESET" pattern at line 5678
     * Log availability: 10.03.24 to 20.03.24 (includes fault date ✓)

3. **Output**:
   - JIRA comment with:
     * Log metadata (dates, versions, serial number)
     * Hansy link for visualization
     * Matched error patterns with line numbers
   - Label changed: EM_Analyzer_PreAnalyzed_auto
   - Assigned to default engineer
   - Dashboard updated with success status

---

## Configuration-Driven Behavior

The system is **highly configurable** through JSON files:

- **feature_config.json**: Controls which JIRA projects, labels, components to process
- **Trace_Patterns_config.json**: Defines error signatures to search for
- **Validation_Patterns_config.json**: Defines validation rules for logs
- **downloadPipe_Patterns_config.json**: Patterns for downloadPipe file analysis

This allows adding new error patterns without code changes!

---

## Error Handling

The system has **robust error handling**:

1. **Validation Errors**: Marks ticket as "need_info" with specific reasons
2. **Processing Errors**: Catches exceptions, logs to Error_log.csv, marks ticket as "Failed"
3. **Partial Success**: Even if some logs fail, processes remaining logs
4. **Metrics Tracking**: Counts processed/succeeded/failed tickets

---

## Summary

This is a **sophisticated automated diagnostic system** that:
- ✅ Integrates with JIRA for ticket management
- ✅ Handles multiple log formats (.pro, .bin, .zip)
- ✅ Decodes binary logs using TRC files
- ✅ Performs intelligent pattern matching to identify issues
- ✅ Generates human-readable diagnostic reports
- ✅ Updates JIRA with findings automatically
- ✅ Tracks metrics via CSV dashboards
- ✅ Handles errors gracefully with comprehensive logging

**Business Value**: Reduces manual log analysis time from hours to minutes per ticket!
