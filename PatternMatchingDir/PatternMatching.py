from Global.global_var import *
from configSettings import *
import os
import re
import datetime
import datefinder
from datetime import date
from datetime import datetime
from datetime import timedelta

def getStringofRE(RE,stringline_to_check):
    matchedString=""
    match_str=re.search(RE,stringline_to_check)
    if(match_str):
        matchedString=str(match_str.group())
    return matchedString

def extractConfigTextPatternstoMatch():
    configTextPatternstoMatch={}
    configTextPatternstoMatch=Global.global_var.g_comment_pattern_config["CommentTextPatterns"][0]
    return configTextPatternstoMatch
        
def extractConfigRePatternstoMatch():
    configRePatternstoMatch={}
    configRePatternstoMatch=Global.global_var.g_comment_pattern_config["CommentREPatterns"][0]
    return configRePatternstoMatch
    
def getLogname(log):
    logName=""
    logName = os.path.basename(log)
    return logName
      
def getLogHandler(log):
    try:
        logHandler=open(log,encoding="utf8",errors='ignore')
    except:
        try:
            logHandler=open(log,encoding="latin-1",errors='ignore')
        except:
            logHandler=open(log,encoding="ISO-8859-1",errors='ignore')
    return logHandler
    
def getSW_IDFromTraces(log,logHandler):
    line = logHandler.readline()
    actual_SW_ID="unknown"
    while line:
            line_check=str(line)
            #swid_str=_SW_ID
            SW_ID_pattern_strings=["<file@card>OSALCORE  \"AI_PRJ_RN_AIVI_","<gen3flex@dlt>(core0)OSALCORE  \"AI_PRJ_RN_AIVI_"]
            #SW_ID_pattern_strings=Global.global_var.g_validation_pattern_config["_SW_ID_inFile"]
            if(SW_ID_pattern_strings[0] in line_check) or (SW_ID_pattern_strings[1] in line_check):
                swid=re.findall('"([^"]*)"', line_check)
                actual_SW_ID=str(swid[0])
                break
            line = logHandler.readline()#handler.close()
    """
    try:
        while line:
            line_check=str(line)
            #swid_str=_SW_ID
            SW_ID_pattern_strings=Global.global_var.g_validation_pattern_config["_SW_ID_inFile"]
            if(SW_ID_pattern_strings[0] in line_check) or (SW_ID_pattern_strings[1] in line_check):
                swid=re.findall('"([^"]*)"', line_check)
                actual_SW_ID=str(swid[0])
                break
            line = logHandler.readline()#handler.close()
    except Exception as e:
        print(str(e))
        print("Error in parsing the file to search SW_IDs :"+str(log))
    """
    return actual_SW_ID
    
"""    
def getCustomerVersion(actual_SW_ID):
    return CustomerVersion
"""

def getLogCollectedDate(log,logHandler,stringMatch,patternMatch):
    logCollectedDate=""
    #global startline
    #global endline
    line = logHandler.readline()
    print("first Line")
    print(line)
    while line:
        line_check=str(line)
        #print(line)
        if(line_check.find(stringMatch)!=-1):
            logCollectedDate=getStringofRE(patternMatch,line_check)
            print(logCollectedDate)
            if(logCollectedDate!=""):
                break
        line = logHandler.readline()
    print("last line")
    print(line)
    print("Log collected date is noted")
    return logCollectedDate
    
def getLogAvailabilityfromtoDate(log,logHandler):
    #global startline
    #global endline
    startline=""
    endline=""
    logAvailabilityDatesLines=[]
    logAvailabilityDates=[]
    logAvailabilityPart=[]
    line = logHandler.readline()
    print("line")
    print(line)
    occurrence_count=0
    line_count=0
    to_date=""
    curr_to_date=""  
    start_date_search=0
    block0date=""
    block0date_noted=False
    while line:
        #print("while 1")
        line_count=line_count+1
        line_check=str(line)
        if(block0date_noted==False):
            block0_match = re.search(r'<......2. ..:..:.. UTC>', line_check)
            if block0_match:
                block0date=str(block0_match.group())
                block0date_noted=True
        if(start_date_search==0):
            block0_pattern=re.search(".*errmemd: ERRMEM beginning of block 1 from device", line_check)
            if(block0_pattern):
                start_date_search=1
                line = logHandler.readline()
                continue
            line_pattern=re.search(".*errmemd: ERRMEM beginning of block [1-9][0-9]?", line_check)
            if not line_pattern:
                #print("while if 1")
                line = logHandler.readline()
                continue
            else:
                start_date_search=1
                block0date=""
                line = logHandler.readline()
                continue
        match = re.search(r'<......2. ..:..:.. UTC>', line_check)
        if match:
            occurrence_count=occurrence_count+1
            #print('found', match.group()) ## 'found word:cat'
            if(occurrence_count==1):
                startline=line_count
                if(block0date==""):
                    logAvailabilityDates.append(str(match.group()))
                else:
                    logAvailabilityDates.append(block0date)
                to_date=logAvailabilityDates[0]
            else:
                endline=line_count
                curr_to_date=str(match.group())
                """
                print("-------------------")
                print("to_date before change "+to_date)
                print("curr_to_date "+curr_to_date)
                """
                if(isToDateFallsAfterFromDate(to_date,curr_to_date)):
                    to_date=curr_to_date
                """
                print("to_date  "+to_date)
                print("-------------------")
                """               
        line = logHandler.readline()
    logAvailabilityDates.append(to_date)
    logAvailabilityPart=[startline,endline]
    print("from_to_date in function")
    print(logAvailabilityDates)
    logAvailabilityDatesLines=[logAvailabilityDates,logAvailabilityPart]
    #except:
        #from_to_date=False
    return logAvailabilityDatesLines

def setLogAvstatusDuringFaultDate(logHandler,logAvailabilityDates,faultOccDate,logAvailabilityLines):
    logAvailabilityfromDate=logAvailabilityDates[0]
    logAvailabilitytoDate=logAvailabilityDates[1]
    logAvailablilty=islogOnFaultDateAvailable(logHandler,faultOccDate)
    dates_InBetween=checkifdateIsBetween(logAvailabilityDates,faultOccDate)
    print("*****")
    print(logAvailablilty)
    print(dates_InBetween)
    print("*****")
    if(logAvailablilty==True and dates_InBetween==True):
        logAvstatusDuringFaultDate=" *** LOGS AVAILABLE ON FAULT OCCURRENCE DATE *** "
    else:
        if(dates_InBetween==True):
            logHandler.seek(0)
            logAroundBoundaryAvailablilty=islogAroundBoundaryFaultDateAvailable(logHandler,logAvailabilityDates,faultOccDate)
            logHandler.seek(0)
            logAroundAvailablilty=islogAroundFaultDateAvailable(logHandler,logAvailabilityDates,faultOccDate,logAvailabilityLines)
            if(logAroundAvailablilty==True or logAroundBoundaryAvailablilty==True):
                logAvstatusDuringFaultDate=" *** LOGS AVAILABLE AROUND FAULT OCCURRENCE DATE *** "
            else:
                logAvstatusDuringFaultDate="*** LOGS MISSING ONLY ON AND AROUND FAULT OCCURRENCE DATE ***"
        else:
            logAvstatusDuringFaultDate="*** LOGS UNAVAILABLE ***"
    return logAvstatusDuringFaultDate  

def islogOnFaultDateAvailable(logHandler,faultOccDate):
    availability=False
    logHandler.seek(0)
    text=logHandler.read()
    if("<"+str(faultOccDate) in text):
        print("Traces available on / around fault occurrence date")
        availability=True
    return availability
    
def isFaultDateOccurWithinAvailabilityDates(logHandler,faultOccDate,logAvailabilityLines):
    linecount=0
    logHandler.seek(0)
    line=logHandler.readline()
    availability=False
    while line:
        linecount=linecount+1
        if(linecount<logAvailabilityLines[0] or linecount<logAvailabilityLines[1]):
            line=logHandler.readline()
            continue
        line_check=str(line)
        if("<"+str(faultOccDate) in line_check):
            availability=True
            break
    return
    
def islogAroundBoundaryFaultDateAvailable(logHandler,logAvailabilityDates,faultOccDate):
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    availability=0
    # dates in string format
    #str_d1_occur = str(faultOccDate)
    #15.05.22
    #<04.05.22 06:03:53 UTC>
    # convert string to date object
    print("########")
    print(faultOccDate)
    str_d_occur = datetime.strptime(str(faultOccDate), "%d.%m.%y")
    print(str_d_occur)
    print("########")
    print(logAvailabilityDates)
    str_d_from = datetime.strptime(str(logAvailabilityDates[0][1:-14]), "%d.%m.%y")
    print(str_d_from)
    str_d_to = datetime.strptime(str(logAvailabilityDates[1][1:-14]),"%d.%m.%y")
    print(str_d_to)

    # difference between dates in timedelta
    delta1 = str_d_occur - str_d_to
    print(f'Difference is {delta1.days} days')
    days_diff1=int(delta1.days)

    # difference between dates in timedelta
    delta1 = str_d_from - str_d_occur
    print(f'Difference is {delta1.days} days')
    days_diff2=int(delta1.days)

    if(((days_diff1 > -3)and(days_diff1 <= 3)) or((days_diff2 > -3)and(days_diff2 <= 3))):
        availability=1
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    return availability
    
def islogAroundFaultDateAvailable(logHandler,logAvailabilityDates,faultOccDate,logAvailabilityLines):
    availability=0
    AroundDateStrings=[]
    AroundDateList=[]
    AroundDateList=getAroundDates(faultOccDate,3)
    AroundDateStrings=convertToStrings(AroundDateList)
    for dateString in AroundDateStrings:
        logHandler.seek(0)
        availability=islogOnFaultDateAvailable(logHandler,faultOccDate)
        if(availability==1):
            print("(+ or - 3 days) Around date available :"+ dateString)
            logHandler.seek(0)
            availability=isFaultDateOccurWithinAvailabilityDates(logHandler,faultOccDate,logAvailabilityLines)
            break
    return availability
    
def getAroundDates(faultOccDate,No_of_Days):
    AroundDateList=[]
    Around_date_plus_List=[]
    Around_date_minus_List=[]
    occurred_date = datetime.strptime(str(faultOccDate), "%d.%m.%y")
    around_date_plus=occurred_date
    around_date_minus=occurred_date
    print('faultOccDate :',occurred_date)
    for day in range(No_of_Days):
        around_date_plus = around_date_plus + timedelta(day+1)
        around_date_minus = around_date_minus - timedelta(day+1)
        Around_date_plus_List.append(around_date_plus)
        Around_date_minus_List.append(around_date_minus)
    Around_date_minus_List.reverse()
    AroundDateList=Around_date_minus_List+Around_date_plus_List
    print("Around Dates List of "+faultOccDate+" : ")
    print(AroundDateList)
    return AroundDateList
    
def convertToStrings(AroundDateList):
    AroundDateStrings=[]
    for around_date in AroundDateList:
        around_date_str=around_date.strftime("%Y-%m-%d")
        around_date_str=around_date_str.split('-')
        new_item_str=around_date_str[2]+"."+around_date_str[1]+"."+around_date_str[0][2:]
        AroundDateStrings.append(new_item_str)
    return AroundDateStrings
    
def isToDateFallsAfterFromDate(fromD,toD):
    #print("######")
    #print(fromD)
    #print(toD)
    #print("######")
    #fromD="<23.12.22 21:14:31 UTC>"
    fromD=fromD[1:-14]
    #print(fromD)
    fromD=fromD.split('.')
    if(fromD[0].startswith('0')):
        fromD[0]=fromD[0][1]
    if(fromD[1].startswith('0')):
        fromD[1]=fromD[1][1]
    fromD[2]="20"+fromD[2]
    #print(fromD)
    #toD="<09.03.22 21:14:31 UTC>"
    toD=toD[1:-14]
    #print(toD)
    toD=toD.split('.')
    if(toD[0].startswith('0')):
        toD[0]=toD[0][1]
    if(toD[1].startswith('0')):
        toD[1]=toD[1][1]
    toD[2]="20"+toD[2]
    #print(fromD)
    #print(toD)
    
    d1 = date(int(fromD[2]),int(fromD[1]),int(fromD[0]))
    d2 = date(int(toD[2]),int(toD[1]),int(toD[0]))

    if d1 <= d2:
        #print("Yes.. True falls after from date")
        return True
    #print("No.. False falls before from date")
    return False

"""
    
def getlogAvailabilitytoDate(log,logHandler,patternMatch):
    return logAvailabilitytoDate
"""
def checkifdateIsBetween(from_to_date,date_dd_mm_yy):
    fromtodate=[]
    result=False
    print("DATE")
    print(from_to_date)
    #---------------
    strn=from_to_date[0]
    str2=strn[1:9]
    print(str2)
    datetimeobj=datetime.strptime(str2,"%d.%m.%y")
    print(datetimeobj)
    fromtodate.append(datetimeobj)
    #-----------------
    strn=from_to_date[1]
    str2=strn[1:9]
    print(str2)
    datetimeobj=datetime.strptime(str2,"%d.%m.%y")
    print(datetimeobj)
    fromtodate.append(datetimeobj)
    strn=str(date_dd_mm_yy)
    print("###")
    print(strn)
    #str2=strn[0:8]
    #print(str2)
    datetimeobj=datetime.strptime(strn,"%d.%m.%y")
    print(datetimeobj)
    fromtodate.append(datetimeobj)
    if(fromtodate[0]<fromtodate[2]<fromtodate[1]):
        result=True
    print(fromtodate)
    return result
    
def getSerialNo(log,logHandler,stringMatch):
    serialNumber="not known"
    #global startline
    #global endline
    line_count=0
    line = logHandler.readline()
    while line:
        line_count=line_count+1
        line_check=str(line)
        if(line_check.find(stringMatch)==-1):
            #print("Serial number line NOT found")
            line = logHandler.readline()
            continue
        else:
            print("Serial number line found")
            start = line_check.find("'") + len("'")
            serialNumber=line_check[start:-2]
            print(serialNumber)
        if(serialNumber!="unknown"):
            break
        else:
            line = logHandler.readline()
    return serialNumber
    
def getPartNo(log,logHandler,stringMatch):
    partNumber="not known"
    #global startline
    #global endline
    line_count=0
    line = logHandler.readline()
    while line:
        line_count=line_count+1
        line_check=str(line)
        if(line_check.find(stringMatch)==-1):
            print("part number line NOT found")
            line = logHandler.readline()
            continue
        else:
            print("part number line found")
            start = line_check.find("'") + len("'")
            partNumber=line_check[start:-2]
            print(partNumber)
        if(partNumber!="unknown"):
            break
        else:
            line = logHandler.readline()
    return partNumber
    
def getOverWrittenBlocks(logHandler):
    blks_overwrtn=""
    #global startline
    #global endline
    line_count=0
    line = logHandler.readline()
    while line:
        line_count=line_count+1
        line_check=str(line)
        if(line_check.find("blocks are missing in device")==-1):
            line = logHandler.readline()
            continue
        else:
            for word in line_check.split():
                if word.isdigit():
                    blks_overwrtn=str(word)
                    print("Overwritten blocks -- noted :"+blks_overwrtn)
                    break
        break
    return blks_overwrtn
    
def find_missing(lst):
    start = lst[0]
    end = lst[-1]
    return sorted(set(range(start, end + 1)).difference(lst))
    
def getMissingBlocks(logHandler):
    list_blks_available=[]
    list_blks_missing=[]
    blks_missing=0
    prev_blk_no=0
    #global startline
    #global endline
    line_count=0
    line = logHandler.readline()
    while line:
        line_count=line_count+1
        line_check=str(line)
        if(line_check.find("ERRMEM beginning of block")!=-1):
            print(line_check)
            for word in line_check.split():
                if(word.isdigit()):
                    number=int(word)
                    if(number!=0):
                        list_blks_available.append(number)
                    break
        line = logHandler.readline()    
    print("list_blks_available:- ")
    print(list_blks_available)
    list_blks_missing=find_missing(list_blks_available)
    print("Missing Blocks")
    print(list_blks_missing)
    print("Missing blocks are noted")
    return list_blks_missing
    
def getMissedLogInfo(log,logHandler,logAvailabilityfromtoDate,faultOccDate):
    try:
        #---
        # Open the file with read only permit
        global missed_traceline
        missed_dateline=[]
        tempstr=""
        templine=""
        line = logHandler.readline()        
        strg=str(faultOccDate)
        #str2=strg[1:9]
        #print(str2)
        datetimeobj=datetime.strptime(strg,"%d.%m.%y")
        print("FROM...")
        print(datetimeobj)
        faultdate=datetimeobj
        print(faultdate)
        
        while line:
            #line_count=line_count+1
            strg=""
            line_check=str(line)
            match = re.search(r'<......2. ..:..:.. UTC>', line_check)
            if match:
                strg=str(match.group())
                str2=strg[1:9]
                datetimeobj=datetime.strptime(str2,"%d.%m.%y")
                if(datetimeobj <= faultdate):
                    tempdate=datetimeobj
                    tempstr=strg
                    templine=line_check
                    line = logHandler.readline()
                else:
                    print("Missed from "+str(tempdate))
                    missed_dateline.append(tempstr)
                    missed_traceline.append(templine)
                    line = logHandler.readline()
                    while line:
                        strg=""
                        line_check=str(line)
                        match = re.search(r'<......2. ..:..:.. UTC>', line_check)
                        if match:
                            strg=str(match.group())
                            str2=strg[1:9]
                            datetimeobj=datetime.strptime(str2,"%d.%m.%y")
                            if(datetimeobj >= faultdate):
                                print("Missed till "+str(datetimeobj))
                                missed_dateline.append(strg)
                                missed_traceline.append(line_check)
                                print("Trace lines:")
                                print(missed_traceline[0])
                                print(missed_traceline[1])
                                return missed_dateline
                        else:
                            line = logHandler.readline()
            else:
                line = logHandler.readline()
    except:
        missed_dateline=False
    missedLogSpecificInfo=[missed_dateline,missed_traceline]
    return missedLogSpecificInfo
       
### Currently not in use ###    
def setAnalysisStatement(logAvstatusDuringFaultDate,overwritten_info,missing_block_info):
    analysisStatement=whatNext=""
    if(logAvstatusDuringFaultDate=="*** LOGS MISSING ONLY ON AND AROUND FAULT OCCURRENCE DATE ***"):
        analysisStatement="Logs encompassing timing of fault but unavailable only on and around failure date"
        whatNext="\n"+"Em_trace doesn't appear to be collected from affected target. Please cross check!"
    else:
        if(overwritten_info!="NA" or missing_block_info!="NA"): 
            analysisStatement="Logs during timing of fault are lost in overwritten / missing errmems blocks and further analysis not possible."
        else:
            analysisStatement="Logs during timing of fault are not available and further analysis not possible."
        whatNext="\n"+"We need logs during the fault for further analysis. Please check if the issue can be reproduced…"
    analysisStatement=analysisStatement+whatNext
    return analysisStatement