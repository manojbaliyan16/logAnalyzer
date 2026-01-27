from TicketDir.Manipulate_TicketData import *
import re
class Ticket:
    def __init__(self,FTMD):
        self.FTMD=FTMD
        return
    ####### VALIDATION OF TICKET ######  
        
    def ValidateTicketData(self):
        VTMD=[]
        status="VALID"
        reasonList=[]
        FTMD=self.FTMD
        print(FTMD)
        VTMD=FTMD
        print("------")
        #print(VTMD)
        relevence=FTMD[2]
        brand=FTMD[3]
        attachmentList=FTMD[4]
        if(attachmentList==[]):
            status="INVALID"
            reason="--> Attachments in the ticket to process"
            reasonList.append(reason)
        else:
            status=self.validateTicketAttachments(attachmentList)
            reasonList.append("--> bin/pro/zipped-bin file type logs attached")
        if(relevence==""):
            status="INVALID"
            reason="--> Relevence information in the ticket"
            reasonList.append(reason)
        if(brand==""):
            status="INVALID"
            reason="--> Brand information in the ticket"
            reasonList.append(reason)
        if(status=="INVALID"):
            VTMD=[status,FTMD[0],reasonList]
        else:
            #print(VTMD)
            VTMD.insert(0,status)
        return VTMD
        
    def validateTicketAttachments(self,attachmentsPathList):
        status="INVALID"
        valid_extensions = [".bin", ".pro", ".txt",".exv",".zip",]

        for path in attachmentsPathList:
            if any(path.endswith(ext) or path.find("downloadPipe") for ext in valid_extensions):
                status = "VALID"
        return status  
        
    ######### MANIPULATION OF TICKETS ###############
    def ManipulateTicketData(self,VTMD,tkt_base_folder_path):
        MTMD=[]
        status=VTMD[0]
        tkt_number=VTMD[1]
        SW_ID=VTMD[2]
        Relevence=VTMD[3]
        Brand=VTMD[4]
        attachmentList=VTMD[5]
        Description=VTMD[6]
        Components=VTMD[9]
        buildVersion=getBuildVersion(SW_ID)
        customerVersion=getCustomerVersion(buildVersion)
        platform=getPlatform(Relevence)
        faultDate=getFaultDate(Description)
        variant=getVariant(Relevence,Brand)
        TRCPath="GetLogs\\NCG3D-305200\\TRCs"
        """
        if((SW_ID not in ["UnknownBoschVersion","UnidentifiedCustVersion","Unidentified Cust Version","Unplanned"])and(customerVersion not in ["","Unavailable"])):
            TRCPath=extractTraceClasses(tkt_base_folder_path,customerVersion,buildVersion,platform,variant)
            if not os.listdir(TRCPath):
                TRCPath="Empty"
                raise Exception("Project specified file (TRCs) could not be fetched. Please check the validity /availablilty of SW ")
        else:
            TRCPath="Undetermined"
            raise Exception("SW ID updated is UNKNOWN ")
        """
        #****** MTMD *******#
        MTMD=[status,tkt_number,SW_ID,customerVersion,buildVersion,platform,Relevence,variant,attachmentList,faultDate,TRCPath,Components]
        #*******************#
        return MTMD
        
   