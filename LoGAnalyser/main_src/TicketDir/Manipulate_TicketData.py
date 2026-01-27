from TicketDir.retreiveCustVersionFromDashboard import *
from TicketDir.getTRC import *
from Global.global_var import *
import shutil
import re
import os
############ Manipulation Helper Function #####################

def getBuildVersion(SW_ID):
    buildVersion=SW_ID[4:]
    return buildVersion
    
def getCustomerVersion(buildVersion):
    customerVersion=""
    try:
        customerVersion=getCustomerVersionFromDashboard(buildVersion,"cc")
        if(customerVersion=="Unavailable"):
            customerVersion=getCustomerVersionFromDashboard(buildVersion,"git")
    except:
        print("Error in retreiving customer version")
        print("Customer Version")
        print(customerVersion)
    return customerVersion
    
def getPlatform(Relevence):
    if(Relevence not in ["Nissan AIVI2-S1","PIVI ST3.1"]):
        platform="gen3"
    else:
        platform="gen4"
    return platform
    
def getVariant(Relevence,Brand):
    if(Relevence == "Nissan AIVI2-S1"):
        variant="AIVI2"
    elif(Relevence == "PIVI ST3.1"):
        variant="PIVI2"
    elif(Relevence == "P-IVI"):
        variant="PIVI"
    else:
        variant=Brand
    return variant
    
def getFaultDate(description):
    faultDate=""
    match = re.search(r'\d{4}\/\d{1,2}\/\d{1,2}',description) 
    if match:
        print("matches bw")
        # date returned will be a datetime.datetime object. here we are only using the first match.
        print("if-else 1")
        dt = str(match.group())
        print(dt)
        dates=dt.split('/')
        print(dates)
        dd=dates[2]
        mm=dates[1]
        yyyy=dates[0]
        yy=yyyy[-2:]
        print(dd)
        print(mm)
        print(yy)
        if(len(dd)==1):
            dd="0"+dd
        if(len(mm)==1):
            mm="0"+mm
        date_dd_mm_yy=str(dd+"."+mm+"."+yy)
        print(date_dd_mm_yy)
        faultDate=date_dd_mm_yy            
    else:
        match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}',description)            
        if match:
            print("matches fw")
            # date returned will be a datetime.datetime object. here we are only using the first match.
            print("if-else 1")
            dt = str(match.group())
            print(dt)
            dates=dt.split('/')
            print(dates)
            dd=dates[0]
            mm=dates[1]
            yyyy=dates[2]
            yy=yyyy[-2:]
            print(dd)
            print(mm)
            print(yy)
            if(len(dd)==1):
                dd="0"+dd
            if(len(mm)==1):
                mm="0"+mm
            date_dd_mm_yy=str(dd+"."+mm+"."+yy)
            print(date_dd_mm_yy)
            faultDate=date_dd_mm_yy            
    return faultDate
    
#NOT USED ANYWHERE
    
def createTicketAnalysisFolder(tkt_number):
    tkt_folder_path=""
    tkt_folder_path=TRCDownloadPath=Global.global_var.g_feature_control_config["DownloadPath"]+tkt_number
    if os.path.exists(tkt_folder_path):
        shutil.rmtree(tkt_folder_path)
    os.mkdir(tkt_folder_path)
    return tkt_folder_path
    
############ TRC Extraction #####################
    
def extractTraceClasses(tkt_folder_path,customerVersion,buildVersion,platform,variant):
    TRCPath=""
    TRCPath=getTRC(tkt_folder_path,customerVersion,buildVersion,platform,variant)
    return TRCPath