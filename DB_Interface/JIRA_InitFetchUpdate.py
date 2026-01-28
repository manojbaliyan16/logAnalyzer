from jira import JIRA, JIRAError  # @IgnorePep8
import Global.global_var
import os
import shutil
#### JIRA Connection #############

def initDB(server,user,password): #connect
    #JIRA server
    #server = "https://hi-cmts.apps.intranet.bosch.com:8443"
    # Login to JIRA
    print("\n Logging into JIRA........")
    jira = JIRA(options={'server': server, 'verify': False}, basic_auth=(str(user), str(password)))
    #print(jira)
    if not jira:
        errormsg = 'Unable to login to JIRA'
        logging.error(errormsg)
        sys.exit(0)
    print("JIRA Connection is successful")
    return jira
    
##### JIRA Query ########

def queryDB(jira_reference,jira_query,maxTickets):
    query_result=[]
    query_result_references=[]
    ticket_ref=[]
    print("jira_query")
    print(jira_query)
    query_result=jira_reference.search_issues(jira_query,maxResults=maxTickets)
    print("query_result")
    print(query_result)
    for ticket in query_result:
        ticket_ref=jira_reference.issue(ticket.key)
        query_result_references.append(ticket_ref)
    return query_result_references       
    
##### Creation of folder with ticket number ########

def createTicketFolder(TicketNo,basefolderpath):
    ticketfoldername=str(TicketNo)
    ticketFolderPath=os.path.join(basefolderpath, ticketfoldername)
    if(os.path.exists(ticketFolderPath)):
        shutil.rmtree(ticketFolderPath)
    os.mkdir(ticketFolderPath)
    return ticketFolderPath
    
#### Downloading of attachments from ticket #########
    
def downloadAttachments(reference,downloadPath):
    ticketFolderPath=os.path.join("GetLogs", "NCG3D-305200")
    downloadAttachmentsInfo=[]
    #ticketFolderPath=createTicketFolder(reference,downloadPath)
    if os.path.exists(ticketFolderPath):
        shutil.rmtree(ticketFolderPath)
    os.mkdir(ticketFolderPath)
    downloadfilespaths=[]
    for attachment in reference.fields.attachment:
        downloadfilepath=os.path.join(ticketFolderPath, attachment.filename)
        if((downloadfilepath.endswith(".pro")) or (downloadfilepath.endswith(".bin")) or 
           (downloadfilepath.endswith(".zip")) or ("downloadPipe" in downloadfilepath) or
           (downloadfilepath.endswith(".dlt")) or (downloadfilepath.endswith(".txt")) or
           (downloadfilepath.endswith((".core", ".dump", ".dmp", ".backtrace")))):
            data = attachment.get()
            with open(downloadfilepath, 'wb') as f:
                f.write(data)
            downloadfilespaths.append(downloadfilepath)
    downloadAttachmentsInfo=[ticketFolderPath,downloadfilespaths]
    return downloadAttachmentsInfo
    

#### Tabulating the ticket meta data retrieved from JIRA #######
    
def frameFTMDT(query_result_references,downloadPath):
    FTMDT=[] # <Ticket No | SW_ID | Relevence | Brand | AttachmentList | Description_with_Fault_Date | AttachmentPath | Ticket reference|Component>
    FTMD=[]
    for reference in query_result_references:
        FTMD.append(str(reference))
        FTMD.append(str(reference.fields.versions[0]))
        FTMD.append(str(reference.fields.customfield_10390[0]))
        FTMD.append(str(reference.fields.customfield_10393[0]))
        downloadAttachmentsInfo=downloadAttachments(reference,downloadPath)
        print("Attachement List:")
        print(downloadAttachmentsInfo[1])
        FTMD.append(downloadAttachmentsInfo[1])
        FTMD.append(str(reference.fields.description))
        FTMD.append(downloadAttachmentsInfo[0]) #Ticket Folder path
        FTMD.append(reference)
        print("Ticket Components")
        componentsList=[]
        for i in range(len(reference.fields.components)):
            componentsList.append(str(reference.fields.components[i]))
        FTMD.append(componentsList)
        FTMDT.append(FTMD)
        FTMD=[]
    print(FTMDT)
    return FTMDT

#### Fetch the ticket data by querying JIRA ###########
    
def fetchFTMDT(DB_reference,DB_query,maxRes,downloadPath):
    print(DB_query)
    print(maxRes)
    #query_result_references=DB_reference.search_issues(DB_query, maxResults=maxRes)
    query_result_references=queryDB(DB_reference,DB_query,maxRes)
    print("query_result_references")
    print(query_result_references)
    print("=======================")
    FTMDT=frameFTMDT(query_result_references,downloadPath)
    return FTMDT
    
####### JIRA Update ########
#PTMDT=[TicketNo,label_to_change,logList,analysis_results,result_comment,default_assignee]
#     [TicketNo,label_to_change,logList,analysis_results,result_comment,default_assignee]
#     [TicketNo,label_to_change,logList,analysis_results,result_comment,default_assignee]


#### Update the ticket analysis results to JIRA ###########

def UpdatePTMDT(DB_reference,PTMDT):
    #PTMD=[FTMD[0],ticket_reference,label_to_change,logList,analysis_results,result_comment,default_assignee]
    #myJira.add_comment(issue_number,analysis_comment)
    for PTMD in PTMDT:
        ticket_reference=PTMD[1]
        attachment_update_status=attachment_updateJIRA(PTMD[3],ticket_reference,DB_reference)
        comment_update_status=comment_updateJIRA(PTMD[4],ticket_reference,DB_reference)
        comment_update_status=comment_updateJIRA(PTMD[5],ticket_reference,DB_reference)
        def_assignee_update_status=default_assignee_updateJIRA(PTMD[6],ticket_reference,DB_reference)
        label_update_status=label_updateJIRA(PTMD[2],ticket_reference,DB_reference)
    return
    
######## NOT USED ##############
    
def SW_IDUpdateJIRA():
    update_status=False
    return update_status
    
    
def attachment_updateJIRA(loglist,ticket_reference,DB_reference):
    update_status=False
    for log in loglist:
        if(log.find("/DirectPro_LOGS/")>=0):
            with open(log,'rb') as f:
                DB_reference.add_attachment(issue=ticket_reference, attachment=f)
            print("!! Decoded File successfully uploaded in JIRA Ticket !!")
    update_status=True
    return update_status
    
def comment_updateJIRA(analysis_comments,ticket_reference,DB_reference):
    update_status=False
    for comment in analysis_comments:
        print("===============")
        print(ticket_reference)
        print(comment)
        DB_reference.add_comment(ticket_reference,comment)
    update_status=True
    return update_status
    
def label_updateJIRA(label_to_change,ticket_reference,DB_reference):
    update_status=False
    global succeeded_ticket_count
    Labels=ticket_reference.fields.labels
    print(Labels)
    for i in range(len(Labels)):
        print(i)
        if((ticket_reference.fields.labels[i]=="Errmem_TBD")or((ticket_reference.fields.labels[i]=="errmem_TBD"))):
            ticket_reference.fields.labels[i]="EM_Analyzer_PreAnalyzed_auto"
            ticket_reference.update(fields={"labels": ticket_reference.fields.labels})            
            print("Label changed as Pre-Analyzed")
    return update_status
    
def default_assignee_updateJIRA(default_assignee,ticket_reference,DB_reference):
    update_status=False
    try:
        print("default_assignee_name : "+default_assignee)
        DB_reference.assign_issue(ticket_reference,default_assignee)
        update_status=True
    except:
        print(default_assignee+":- "+"No such JIRA user is found to assign")
    return update_status
    
##########################
