from Global.global_var import *
import datetime
import os
import re
import datefinder
from datetime import date
from datetime import datetime

def iteratePattern(tracePattern_dict,log,logHandler,faultOccDate,Components=None):
    pattern_count=0
    tracePatternInfo=[[],[]]
    tracePatternParameters=["",""]
    matchedTracePatternText=""
    recommendedComponentToAnalyze=[]
    print("tracePattern_dict")
    print(tracePattern_dict)
    for trace_pattern in tracePattern_dict:
        stat=False
        print(" In for 1")
        patternstring=str(tracePattern_dict[pattern_count]["PATTERN"])
        print(patternstring)
        logHandler.seek(0)
        if Components is None:
            _listpatternsmatched=checkForPattern(patternstring,logHandler,tracePattern_dict,faultOccDate,pattern_count)
        else:
            if str(tracePattern_dict[pattern_count]["COMPONENT_RESP"])!="SW_SWUPDATE":
                continue
            _listpatternsmatched=checkForPattern(patternstring,logHandler,tracePattern_dict,faultOccDate,pattern_count,"SW_SWUPDATE")
        if(_listpatternsmatched!=[]):
            print("list patterns matched")
            print(_listpatternsmatched)
            matchedTracePatternText=frameMatchedPatternsText(_listpatternsmatched)#_listpatternsmatched Line No: "\n"+"Observed Date and Time : "\n"+str(dictn["pattern_matched"])
            tracePatternInfo[0].append(matchedTracePatternText)
        pattern_count=pattern_count+1
    
    tracePatternParameters=tracePatternInfo

    #tracePatternParameters[0]=tracePatternInfo[0]
    #tracePatternParameters[1]=getRecommendedComponentToAnalyze(tracePatternInfo[1])
    #tracePatternInfo.append(matchedTracePatternText)
    #tracePatternInfo.append(recommendedComponentToAnalyze)
    print("tracePatternParameters")
    print(tracePatternParameters)
    print(tracePatternParameters)
    return tracePatternParameters
    
def checkForPattern(patternstring,logHandler,tracePattern_dict,faultOccDate,pattern_count,Components=None):
    _listpatternsmatched=[]
    traceptrn_dict={}
    occur_count=0
    line_count=0
    print("@@@@@@ started checking patterns : ")
    tracepatternsoccurrencedate=""
    line = logHandler.readline()
    while line:
        line_count=line_count+1
        line_check=str(line)
        match = re.search(r'<......2. ..:..:.. UTC>', line_check)
        if match:
            tracepatternsoccurrencedate=str(match.group())
            line = logHandler.readline()
            continue
        if(patternstring in line_check):
            print("line7...$")
            print(tracepatternsoccurrencedate)
            print("faultOccDate for isTracePatternDatearoundFaultOccurrence -- ")
            print(faultOccDate)
            #if(faultOccDate!=""):
            if Components is None:
                if(isTracePatternDatearoundFaultOccurrence(tracepatternsoccurrencedate,faultOccDate)): # + or - 3 days
                    tracelinenumber=line_count
                    #print(tracePattern_dict)
                    #print("pattern_matched")
                    #print(str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]))
                    traceptrn_dict={'lineno':tracelinenumber,"date_occurred":tracepatternsoccurrencedate,"pattern_matched":str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]),"component_respo":str(tracePattern_dict[pattern_count]["COMPONENT_RESP"])}
                    _listpatternsmatched.append(traceptrn_dict)
                    traceptrn_dict={}
                    occur_count=occur_count+1
            else:
                if(Components != "SW_SWUPDATE" or faultOccDate!=""):
                    print(faultOccDate)
                    if( isTracePatternDatearoundFaultOccurrence(tracepatternsoccurrencedate,faultOccDate)): # + or - 3 days
                        tracelinenumber=line_count
                        #print(tracePattern_dict)
                        #print("pattern_matched")
                        #print(str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]))
                        traceptrn_dict={'lineno':tracelinenumber,"date_occurred":tracepatternsoccurrencedate,"pattern_matched":str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]),"component_respo":str(tracePattern_dict[pattern_count]["COMPONENT_RESP"])}
                        _listpatternsmatched.append(traceptrn_dict)
                        traceptrn_dict={}
                        occur_count=occur_count+1
                else:
                    tracelinenumber=line_count
                    #print(tracePattern_dict)
                    #print("pattern_matched")
                    #print(str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]))
                    traceptrn_dict={'lineno':tracelinenumber,"date_occurred":tracepatternsoccurrencedate,"pattern_matched":str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]),"component_respo":str(tracePattern_dict[pattern_count]["COMPONENT_RESP"])}
                    _listpatternsmatched.append(traceptrn_dict)
                    traceptrn_dict={}
                    occur_count=occur_count+1                

        line = logHandler.readline()
    print("_listpatternsmatched")
    print(_listpatternsmatched)
    return _listpatternsmatched
    
def isTracePatternDatearoundFaultOccurrence(tracepatternsoccurrencedate,_fault_occurrence_date):
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(_fault_occurrence_date)
    print(tracepatternsoccurrencedate)

    # dates in string format
    str_d1 = str(_fault_occurrence_date)
    str_d2 = str(tracepatternsoccurrencedate)
    if(tracepatternsoccurrencedate==""):
        return False
    str_d2=str_d2[1:-14].split(' ')[0]
    #15.05.22
    #<04.05.22 06:03:53 UTC>
    # convert string to date object
    d1 = datetime.strptime(str_d1, "%d.%m.%y")
    d2 = datetime.strptime(str_d2, "%d.%m.%y")

    # difference between dates in timedelta
    delta = d2 - d1
    print(f'Difference is {delta.days} days')
    days_diff=int(delta.days)

    if(days_diff in range(-3,3)):
        print("Around 5 days")
        return True
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    return False
    
def frameMatchedPatternsText(_listpatternsmatched):
    matchedTracePatternText=""
    match_count=0
    print(_listpatternsmatched)
    unique_pattern=[]
    for dictn in _listpatternsmatched:
        print("dictn ")
        print(dictn)
        if str(dictn["pattern_matched"]) in unique_pattern:
            continue
        else:
            matchedTracePatternText=matchedTracePatternText+"\n\n"
            matchedTracePatternText=matchedTracePatternText+"Line No: "+str(dictn["lineno"])+"\n"+"Observed Date and Time : "+str(dictn["date_occurred"])+"\n"+str(dictn["pattern_matched"])
            unique_pattern.append(str(dictn["pattern_matched"]))
        match_count=match_count+1
    return matchedTracePatternText
    
def getRecommendedComponentToAnalyze(componentList):
    recommendedComponentToAnalyze=""
    if(componentList==[]):
        recommendedComponentToAnalyze="UNKNOWN"
    else:
        componentList = list(dict.fromkeys(componentList))
        componentList=",".join(map(str,componentList))
        print(componentList)        
    return recommendedComponentToAnalyze

def updatePattern(logHandler):
    line = logHandler.readline()    
    zeroCheck=False
    successCheck=False
    line_count=0
    zeroCount=0
    zeroLine=""
    success_count=[]
    success_line=[]
    ptrn1="block 0 from device /home/root/errmem"
    ptrn2="Update to AI_PRJ_................ SUCCESS"
    print("in update pattern")
    print(str(line))
    res=""
    while line:
        line_count=line_count+1
        line_check=str(line)                 
        if ptrn1 in line_check :
            zeroCheck=True
            zeroCount=line_count
            zeroLine=line_check
        match = re.search(ptrn2,line_check)
        if match:
            successCheck=True
            '''
            if successCheck==True:
                print("matched update")
                print(line_count)
                print(line_check) 
                '''
            success_count.append(line_count)
            success_line.append(line_check) 
            successCheck=False         
        line = logHandler.readline()
    if zeroCheck and len(success_line)==1:
        res="\n\n"+"Line No: "+str(zeroCount)+"\n"+zeroLine+"\n"+"Line No:"+str(success_count[0])+"\n"+success_line[0]+"\n"
        res=res+"Only dummy update has taken place. This is not a SWUpdate issue."
    elif not zeroCheck and success_count!=[] :
        for i in range(len(success_count)):
            res+="\n\n"+"Line No: "+str(success_count[i])+"\n"+success_line[i]+"\n"
            res+="Update is successful."
    print(res)
    return res