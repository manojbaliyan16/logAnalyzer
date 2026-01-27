from configSettings import *
from Global.global_var import *
import subprocess
import os
import shutil

def getTRC(tkt_folder_path,customerVersion,buildVersion,platform,variant):
    status="FAILURE"
    TRCFinderPath=Global.global_var.g_feature_control_config["TRCFinderPath"]
    TRCDownloadPath=createTRCFolder(tkt_folder_path)
    trcFinderArgumentList=[TRCFinderPath,"-b",buildVersion,"-c",customerVersion,"-v",variant,"-p",platform,"-o",TRCDownloadPath]
    try:
        status=triggerTRCFinder(trcFinderArgumentList)
    except Exception as e:
        print("TRC Exception")
        print(str(e))
    print("Status:"+str(status))
    print(TRCDownloadPath)
    print(TRCFinderPath)
    return TRCDownloadPath
    
def createTRCFolder(tkt_folder_path):
    TRCDownloadPath=tkt_folder_path+"\\TRCs"
    if os.path.exists(TRCDownloadPath):
        shutil.rmtree(TRCDownloadPath)
    os.mkdir(TRCDownloadPath)
    return TRCDownloadPath
    
def triggerTRCFinder(trcFinderArgumentList):
    status="SUCCESS"
    getTRCprocess=subprocess.Popen(trcFinderArgumentList)
    status_wait=getTRCprocess.wait()
    comp_status=getTRCprocess.returncode
    if comp_status:
        #####writeFailureLog(issue_number,"TRC Finder is getting failed due to invalid version / variant information in the ticket") #TO ASSIGNEE
        print("TRC Finder is getting failed!")
        print("Invalid version / variant information as arguments")
        #sys.exit(0)
        status="FAILURE"
    return status