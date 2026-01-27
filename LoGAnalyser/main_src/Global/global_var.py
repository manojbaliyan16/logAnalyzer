def Init():
    global g_feature_control_config
    g_feature_control_config=[]
    global g_validation_pattern_config
    g_validation_pattern_config=[]
    global g_comment_pattern_config
    g_comment_pattern_config=[]
    global g_trace_pattern_config
    g_trace_pattern_config=[]
    global g_downloadPipe_pattern_config
    g_downloadPipe_pattern_config=[]
    return

"""
global g_getLogsBaseFolder
g_getLogsBaseFolder="GetLogs\\"
global g_HANSY_TOOL_LINK
g_HANSY_TOOL_LINK="http://fe0vm20pemaivi.de.bosch.com:8083/"

def init():
    #global g_feature_control_dict={}
    #global g_commentDataList=[]
    global g_toDBType
    g_toDBType="JIRA"
    global g_toTakeLabelledTickets
    g_toTakeLabelledTickets=False
    global g_isPreAnalysisRequired
    g_isPreAnalysisRequired=False
    global g_isMainAnalysisRequired
    g_isMainAnalysisRequired=False
    global g_toUploadfile
    g_toUploadfile=False
    global g_toUploadComment
    g_toUploadComment=False
    global g_toBeDefaultAssigned
    g_toBeDefaultAssigned=False
    global g_defaultAssignee
    g_defaultAssignee=""
    return

 HANSY_TOOL_LINK="http://fe0vm20pemaivi.de.bosch.com:8083/"
issue=""
feature_control_dict={}
commentDataList=[]
_toUploadfile=False
_toUploadComment=False

## CONFIG VAIABLES ##
pre_analysis = False
labelled_tickets_processing = False

main_analysis = False
JIRA_updater = False
_myJira=""

#
getlogTicketFolderPath="Getlogs\\"
emtraceprofilepath=""
trcsfilepath=""
_downloaded_decoded_file=""

# IDENTIFIER VALUES (Decoder) ###
_fault_occurrence_date=""
_SW_ID=""
_customerVersion=""
_Relevence=""
_platform=""
_Traces_SW_ID=""
#----

## IDENTIFIER VALUES (Pre-Analyzer) ###

_decoded_filename=""
_availableLog_startDate=""
_availableLog_endDate=""
_hansylink=""
_logCollectedDate=""
_overwrittenBlocks=""
_missingBlocks=""
_logs_unavailability_reason=""
_part_number=""
_serial_number=""
_lastShutdownDate=""
_targetoff_fromDate=""
_targetoff_tillDate=""
_targetoff_traceline1=""
_targetoff_traceline2=""


## IDENTIFIER VALUES (Main Analyzer) ###
_tracepatternsmatched=""
#_tracelinenumber
#_tracepatternsoccurrencedate
_listpatternsmatched=[]

#DASHBOARD COUNTS
processed_ticket_count=0
failed_ticket_count=0
succeeded_ticket_count=0

## LOG RESULT EVENTS ###
eventsDictionary={
"LOGS_AVAILABLE":False,
"LOGS_UNAVAILABLE":False,
"LOGS_AVAILABLE_WITH_MATCHED_TRACE_PATTERNS":False,
"LOGS_UNAVAILABLE_DUE_TO_MISSING_BLOCKS":False,
"LOGS_UNAVAILABLE_DUE_TO_OVERWRITTEN_BLOCKS":False,
"LOGS_DATE_OF_COLLECTION_AVAILABLE":False,
"LOGS_UNAVAILABLE_DUE_TO_MISSING_AND_OVERWRITTEN_BLOCKS":False,
"LOGS_MISSED_DURING_FAULT_DATE":False
}

### JIRA Access ####

jira_id=""
startline=0
endline=0
missed_traceline=[]

### Tickets Log ###
_Tickets_Log=[]
_Tickets_Log_columns = ["Sl_No","Ticket Number","Processed_Status","Date of Build"]
_Tickets_Log_count=1
today = date.today()
date_of_build = today.strftime("%d/%m/%Y")
"""