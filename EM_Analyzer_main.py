#import Global.global_var
print("--total_tickets--")
from Global.global_var import *
from configSettings import *
from tabulate import tabulate
from DB_Interface.DB_Interfacing import *
from TicketFactoryDir.TicketFactory import *
from TicketDir.Ticket import *
from LogsDir.Logs import *
from AnalyzerDir.Analyzer import *
from Dashboard_UpdaterDir.DashBoard_Updater import *
from BuildLogCreatorDir.BuildLogCreator import *
import datetime
import sys
import traceback
#sys.stdout = open('consoleLog.dat', 'w',encoding="utf-8")
total_tickets=0

### CONFIG SETTINGS #####
#create folder for logs if it doesn't exist already
cs=configSettings()
Global.global_var.g_feature_control_config=cs.getFeatureControlConfig()
Global.global_var.g_validation_pattern_config=cs.getValidationPatternConfig()
Global.global_var.g_trace_pattern_config=cs.getTracePatternConfig()
Global.global_var.g_downloadPipe_pattern_config=cs.getdownloadPipePatternConfig()
cs.createGetLogsFolder()

### DB INTERFACE (Fetch) ######
FTMDT=[] # Fetched Tickets Meta Data Table  <Ticket No | SW_ID | Relevence | Brand | Description_with_Fault_Date | AttachmentPath>
INVTMDT=[] #Invalid Tickets Meta Data Table
#initialise vars
db_inf=DBInterfacing(Global.global_var.g_feature_control_config["Server"],Global.global_var.g_feature_control_config["user"],Global.global_var.g_feature_control_config["password"])
#connect to jira, create an instance DB-reference
DB_reference=db_inf.initializeDB() 
#generate a query with project name and labels: "project =ProjectName AND labels in (LN1) OR labels in (LN2)" (format might be diff)
'''
if config=True:
    DB_query=db_inf.generateDBQuery(Global.global_var.g_feature_control_config["ProjectName"],Global.global_var.g_feature_control_config["Labels to process"],Global.global_var.g_feature_control_config["Component to process"])
else:
    DB_query=db_inf.generateDBQuery(Global.global_var.g_feature_control_config["ProjectName"],Global.global_var.g_feature_control_config["Labels to process"])
'''
DB_query=db_inf.generateDBQuery(Global.global_var.g_feature_control_config["ProjectName"],Global.global_var.g_feature_control_config["Labels to process"],Global.global_var.g_feature_control_config["Component to process"])
#fetch ticket data by querying jira and tabulate metadata(list of lists)
FTMDT=db_inf.fetchDB(DB_query,Global.global_var.g_feature_control_config["Maximum Tickets"],Global.global_var.g_feature_control_config["DownloadPath"])
#print(tabulate(FTMDT))
print("total_tickets")

#### TICKET FACTORY INITIALIZATION #######
total_tickets=len(FTMDT)
print(total_tickets)
print(FTMDT[0])
#instance of ticket factory by passing fetched ticket metadata
tkt_fac=TicketFactory(FTMDT)


#### TICKET METRICS ############
PROCESSED_TICKET_COUNT=0
SUCCEEEDED_TICKET_COUNT=0
FAILED_TICKET_COUNT=0
ERROR_LOGS=[]
ERROR_LOG_INFO=[]
processing_tktNo="ARTA Processing"
error=""
ticket_reference="ARTA Ticket Processing"


###### TICKET DATA VALIDATION,MANIPULATION #####
PTMDT=[] #Processed Ticket Metadata Table

for index in range(total_tickets):
    #try:
    PROCESSED_TICKET_COUNT=PROCESSED_TICKET_COUNT+1
    PTMD=[]
    label_to_change=""
    default_assignee=Global.global_var.g_feature_control_config["Default Assignee"]
    req_labels=Global.global_var.g_feature_control_config["Labels to process"]
    print("req_labels")
    print(req_labels)
    result_comment="FAILED"
    info_needed_comment="NA"
    analysis_results=[]
    FTMD=[]
    logList=[]
    
    #### PICK A TICKET FROM SET OF TICKETS / FIELD CLAIMS
    #obtain ref to ticket, its base folder
    FTMD=tkt_fac.pickTicket(index)
    ticket_reference=FTMD[7] #contains all ticket info
    tkt_base_folder_path=FTMD[6]
    print(ticket_reference)
    print(tkt_base_folder_path)
    tkt=Ticket(FTMD) 
    
    #### VALIDATE THE PICKED TICKET ####
    
    VTMD=tkt.ValidateTicketData() #check if required fields and attachment are available.. VTMD<status,tktno,swid...>
    print(VTMD)
    if(VTMD[0]=="INVALID"):
        INVTMDT.append(VTMD)
        info_needed_comment="** Automated Analysis is not supported due to the below information are not getting interpreted ***"+"\n"
        print(VTMD[2])
        for reason in VTMD[2]:
            info_needed_comment=[info_needed_comment+"\n"+str(reason)]
        #Intimate invalid input from the ticket
        analysis_results.append(info_needed_comment)
        label_to_change="EM_Analyzer_need_info"
        PTMD=[FTMD[0],label_to_change,logList,analysis_results,result_comment,default_assignee] #add invalid tickets to PTMDT
        result_comment="Info Needed"
        PTMDT.append(PTMD)
        #print(PTMDT)
        continue
        
    #### MANIPULATE THE TICKET DATA AND GET ADDITIONALLY REQUIRED DATA ####
    
    MTMD=tkt.ManipulateTicketData(VTMD,tkt_base_folder_path) #gets customerVersion,buildVersion,platform,variant,fault occurrence date and downloads attachments
    print("**** MTMD ****")
    print(MTMD) #MTMD=[status,tkt_number,SW_ID,customerVersion,buildVersion,platform,Relevence,variant,attachmentList,faultDate,TRCPath,Component]
    
    #### DOWNLOAD LOGS FROM TICKET #####
    log=Logs(MTMD,tkt_base_folder_path)
    logList=log.getLogs() #logList----> [renamed_validatedProList,renamed_decodedBinList] [validLogList,invalidPros+invaliddecPros]
    print("logList - EM Main")
    print(logList)
    
    ##### ANALYSIS OF DOWNLOADED LOGS #####
    analysis=Analyzer(logList,MTMD[9],MTMD[4],MTMD[3],MTMD[11])
    '''
    if config=True:
        analysis=Analyzer(logList,MTMD[9],MTMD[4],MTMD[3],MTMD[11])
    else:
        analysis=Analyzer(logList,MTMD[9],MTMD[4],MTMD[3]) #faultdate, buildver,customerver, component
    '''
    
    ##### RETREIVAL OF ANALYSIS RESULTS OF THE LOGS #####
    logResults=analysis.analyzeLogs()
    analysis_results.append(logResults)
    print("in main log results")
    print(analysis_results)
    
    ##### UPDATE OF THE TICKET INFORMATION POST ANALYSIS ####
    label_to_change="EM_Analyzer_PreAnalyzed_auto"
    result_comment="SUCCESS"
    SUCCEEEDED_TICKET_COUNT=SUCCEEEDED_TICKET_COUNT+1
    PTMD=[FTMD[0],ticket_reference,label_to_change,logList[2]+logList[0]+logList[1],analysis_results,result_comment,default_assignee]
    #print("==== PTMD ====")
    #print(PTMD)
    PTMDT.append(PTMD)
    
    """
    except Exception as e:
        processing_tktNo=str(ticket_reference)
        label_to_change="EM_Analyzer_Failed"
        result_comment="FAILED"
        FAILED_TICKET_COUNT=FAILED_TICKET_COUNT+1
        error=traceback.format_exc()
        ERROR_LOG_INFO.append([processing_tktNo,error,"Processing Error"])
        ERROR_LOGS.append([processing_tktNo,error,"Processing Error"])
        print("====")
        print(ERROR_LOGS)
        processing_tktNo=""
        error=""
        ERROR_LOG_INFO=[]
    """ 
### DB INTERFACE (Update) -- TICKET ANALYSIS RESULT UPDATE TO DB ###
try:
    if(PTMDT!=[]):
        ticketIndex=logIndex=0
        for PTMD in PTMDT: #PTMD=[FTMD[0],ticket_reference,label_to_change,logList[0]+logList[1],analysis_results,result_comment,default_assignee]
            try:
                analyzedLogList=PTMD[3] #logList 
                print("Analyzed loglist")
                print(analyzedLogList)
                UpdateResultList=PTMD[4] #analysisComment
                print("UpdateResultList")
                print(UpdateResultList)
                for log in analyzedLogList:
                    print(ticketIndex)
                    print(logIndex)
                    print(log)
                    ################# UPDATE OF COMMENT AND ATTACHMENT IN JIRA ########################                    
                    DB_reference.add_comment(PTMD[1],str(UpdateResultList[ticketIndex][logIndex]))
                    print(str(UpdateResultList[ticketIndex][logIndex]))
                    print("LOG PATH -- /DirectPro_LOGS/")
                    print(log)
                    if((("_directPro.pro" not in log) and ("downloadPipe" not in log) and (not log.endswith(".bin"))) or (log.endswith("decoded_auto_invalid.pro"))):
                        with open(log,'rb') as f:
                            DB_reference.add_attachment(issue=PTMD[1], attachment=f)
                            print("!! Decoded File successfully uploaded in JIRA Ticket !!")
                    logIndex=logIndex+1
                    ####################################################################################
                Labels=PTMD[1].fields.labels
                print(Labels)
                for i in range(len(Labels)):
                    print(i)
                    ################# UPDATE OF LABEL IN JIRA ########################
                    if(PTMD[1].fields.labels[i] in req_labels):
                        print(" label to change is available in the list")
                        PTMD[1].fields.labels[i]=str(PTMD[2])
                        PTMD[1].update(fields={"labels": PTMD[1].fields.labels})            
                        print("Label changed as Pre-Analyzed")
                        break
                    ################# UPDATE OF LABEL IN JIRA ########################
                ticketIndex=ticketIndex + 1
                DB_reference.assign_issue(PTMD[1],PTMD[6])
            except Exception as e:
                error=str(e)
                ERROR_LOGS.append([PTMD[1],error,"RESULT UPDATE ERROR"])                
        
    ########### DASHBOARD INITIALIZATION #################
    METRICS=[PROCESSED_TICKET_COUNT,SUCCEEEDED_TICKET_COUNT,FAILED_TICKET_COUNT]
    dashboardRef=Dashboard_Updater(PTMDT,METRICS)
    dashboardRef.updateDataDashboard()
    dashboardRef.updateMetricsDashboard()
    ######################################################
except Exception as e:
    error=str(e)
    ERROR_LOGS.append(["ARTA FAILURE",error,"SERVER INTERFACE / ACCESS ERROR"])

################### WRITING OF BUILD LOGS ################    
if(ERROR_LOGS != []):
    print("******")
    print("Error Log has content")
    today = date.today()
    date_of_build = today.strftime("%d/%m/%Y")
    errorLogRef=BuildLogCreator(ERROR_LOGS,date_of_build)
    errorLogRef.writeBuildLog()
##########################################################
sys.stdout.close()