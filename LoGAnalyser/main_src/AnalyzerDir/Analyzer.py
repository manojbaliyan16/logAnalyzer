from PatternMatchingDir.PatternMatching import *
from PatternMatchingDir.TracePatternMatching import *
from AnalyzerDir.HansyLink import *
from TicketDir.Manipulate_TicketData import *
class Analyzer:
    def __init__(self,logList,faultOccDate,buildVersion,CustomerVersion,Component=None):
        self.logList=logList
        self.faultOccDate=faultOccDate
        self.buildVersion=buildVersion
        self.CustomerVersion=CustomerVersion
        if Component is not None:
            self.Component=Component
        else:
            self.Component=None
        self.commentParameters={}
        return
        
    def analyzeLogs(self):
        logsAnalysisResultsList=[]
        logResult=[]
        downloadPipeResult=""
        print("logList[0]")
        print(self.logList[0])
        print("logList[1]")
        print(self.logList[1])
        if self.Component is not None and "SW_SWUPDATE" in self.Component:
            print("logList[2]")
            print(self.logList[2])
            for log in self.logList[2]:
                print("Analyzing "+log)
                downloadPipeResult=self.analyzeDownloadPipe(log)
                print("in analyze")
                print(downloadPipeResult)
                logsAnalysisResultsList.append(downloadPipeResult)
        for log in self.logList[0]:
            print("Analyzing Log..")
            print(log)
            logResult=self.analyzeLog(log)# logResult=[status,analysis_result]
            logsAnalysisResultsList.append(logResult)
            print("\n\n")
            print("logsAnalysisResultsList")
            print(logsAnalysisResultsList)
            print("\n\n")
        
        for log in self.logList[1]:
            proFile=log
            if("invalid.pro" in log):
                proFile=log.replace("invalid.pro",".pro")
            logResult=" "+proFile+" : The decoded file is inappropriate and is not in interpretable format. Required to check with the validity of SW Version / TRC used to decode."
            logsAnalysisResultsList.append(logResult)
        print("logsAnalysisResultsList")
        print(logsAnalysisResultsList)
        return logsAnalysisResultsList
        
    def analyzeLog(self,log):
        logResult=[]
        commentPatternsMatched={}
        tracePatternsMatchedListAsText=[]
        recommendedComponentsToAnalyze=[]
        #self.commentParameters=[]
        traceParameters=[]
        #if ends with bin, then log result is could not process
        if(log.endswith(".bin")):           
            sub2 = "Downloaded_ZIPS"
             
            # getting index of substrings
            idx2 = log.find(sub2)
             
            # length of substring 1 is added to
            # get string from next character
            idx3 = idx2+len(sub2)+1
            idx4 = log.find("zipped_bin")
            res = log[idx3:idx4-1]+".bin"            
            logResult=" Could not process the log : " + res + " - as TRCs are unavailable in or not accessible from the server"
            return logResult
        logHandler=getLogHandler(log)
        commentPatternsMatched=self.getMatchedCommentpatterns(log,logHandler)
        logAvstatusDuringFaultDate=commentPatternsMatched["logAvstatusDuringFaultDate..."]
        if(logAvstatusDuringFaultDate in ("*** LOGS MISSING ONLY ON AND AROUND FAULT OCCURRENCE DATE ***","*** LOGS UNAVAILABLE ***")):
            overwritten_info=commentPatternsMatched["OverWritten Blocks..........."]
            missing_block_info=commentPatternsMatched["Missing Blocks..............."]
            self.commentParameters=self.deriveCommentParameters(commentPatternsMatched,logAvstatusDuringFaultDate,overwritten_info,missing_block_info)
        else:
            self.commentParameters=commentPatternsMatched
        logHandler=getLogHandler(log)
        if (self.faultOccDate!="") or (self.Component is not None and"SW_SWUPDATE" in self.Component):
            tracePatternsInfo=self.getMatchedTracePatternsList(log,logHandler)
            tracePatternsMatchedListAsText=tracePatternsInfo[0]
            recommendedComponentsToAnalyze=tracePatternsInfo[1]
        commentParametersEvaluated=self.commentParameters
        print(" line 1")
        logResult=self.frameLogResult(commentParametersEvaluated,recommendedComponentsToAnalyze,tracePatternsMatchedListAsText)
        print("in analyze log for update res")
        updateRes=updatePattern(logHandler)
        print(updateRes)
        print("logresult")
        print(logResult)
        logResult=logResult+"\n"+updateRes
        self.closeLogHandler(logHandler)
        return logResult
    """
        
    def getLogHandler(self,attachment_path):
        attachmentHandler="Invalid File"
        try:
            attachmentHandler=open(attachment_path,encoding="utf8",errors='ignore')
        except:
            try:
                attachmentHandler=open(attachment_path,encoding="latin-1",errors='ignore')
            except:
                attachmentHandler=open(attachment_path,encoding="ISO-8859-1",errors='ignore')
        return attachmentHandler
        
    """
        
    def getMatchedCommentpatterns(self,log,logHandler):
        faultOccDate=logName=actual_SW_ID=actual_CustomerVersion="NA"
        logCollectedDate=logAvailabilityfromDate=logAvailabilitytoDate=logAvstatusDuringFaultDate="NA"
        hansyLink=serialNo=partNo="NA"
        missedLogSpecificInfo=[]
        suspicious_entries=0
        overWrittenBlocks=missingBlocks="NA"
        commentPatternsMatched={}
        configTextPatternstoMatch={}
        configRePatternstoMatch={}
        #configTextPatternstoMatch=extractConfigTextPatternstoMatch()
        #configRePatternstoMatch=extractConfigRePatternstoMatch()
        faultOccDate=self.faultOccDate
        logName=getLogname(log)        
        actual_SW_ID=getSW_IDFromTraces(log,logHandler)
        if(actual_SW_ID!=self.buildVersion):
            self.buildVersion=actual_SW_ID
        self.CustomerVersion=getCustomerVersion(actual_SW_ID)
        logCollectedDate=getLogCollectedDate(log,logHandler,"DLT:",r'..../../..')
        print("** logCollectedDate")
        if(logCollectedDate==""):
            logCollectedDate="Unavailable"
        print(logCollectedDate)
        commentPatternsMatched["logName"]=logName
        print(logName)
        logHandler=self.resetLogHandlerToStartOfFile(logHandler)
        logAvailabilityfromtoDate=getLogAvailabilityfromtoDate(log,logHandler)
        print("logAvailabilityfromtoDate")
        print(logAvailabilityfromtoDate)
        actual_CustomerVersion=self.CustomerVersion
        logHandler=self.resetLogHandlerToStartOfFile(logHandler)
        hansyLink=createHansyLink(log)
        if(faultOccDate!=""):
            logAvstatusDuringFaultDate=setLogAvstatusDuringFaultDate(logHandler,logAvailabilityfromtoDate[0],faultOccDate,logAvailabilityfromtoDate[1])
            print("logAvstatusDuringFaultDate")
            print(logAvstatusDuringFaultDate)
            if(logAvstatusDuringFaultDate in ("*** LOGS MISSING ONLY ON AND AROUND FAULT OCCURRENCE DATE ***","*** LOGS UNAVAILABLE ***")):
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                overWrittenBlocks=getOverWrittenBlocks(logHandler)
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                missingBlocks=getMissingBlocks(logHandler)        
            if(logAvstatusDuringFaultDate=="*** LOGS MISSING ONLY ON AND AROUND FAULT OCCURRENCE DATE ***"):
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                serialNo=getSerialNo(log,logHandler,"ERRMEM: VERSIONINFO: EcuSerialNumber:")
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                partNo=getPartNo(log,logHandler,"ERRMEM: VERSIONINFO: EcuSparePartNumber:")
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                missedLogSpecificInfo=getMissedLogInfo(log,logHandler,logAvailabilityfromtoDate[0])
        else:
            faultOccDate= "UNKNOWN or Not in interpretable format (dd/mm/yyyy,yyyy/mm/dd,d/m/yyyy,m/d/yyyy)"  
            if self.Component is not None and "SW_SWUPDATE" in self.Component:
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                overWrittenBlocks=getOverWrittenBlocks(logHandler)
                logHandler=self.resetLogHandlerToStartOfFile(logHandler)
                missingBlocks=getMissingBlocks(logHandler)    
        commentPatternsMatched=self.fillCommentPatternsMatched(faultOccDate,logName,actual_SW_ID,actual_CustomerVersion,logCollectedDate,logAvailabilityfromtoDate[0],logAvstatusDuringFaultDate,hansyLink,serialNo,partNo,overWrittenBlocks,missingBlocks,missedLogSpecificInfo,suspicious_entries)
        return commentPatternsMatched
        
    def fillCommentPatternsMatched(self,faultOccDate,logName,actual_SW_ID,actual_CustomerVersion,logCollectedDate,logAvailabilityfromtoDate,logAvstatusDuringFaultDate,hansyLink,serialNo,partNo,overWrittenBlocks,missingBlocks,missedLogSpecificInfo,suspicious_entries):
        commentPatternsMatched={}
        commentPatternsMatched["Fault Occurrence Date........"]=faultOccDate
        commentPatternsMatched["Log Name....................."]=self.getOriginalLogName(logName)
        commentPatternsMatched["Actual SW_ID................."]=actual_SW_ID
        commentPatternsMatched["Actual_CustomerVersion......."]=actual_CustomerVersion
        commentPatternsMatched["Log Collected Date..........."]=logCollectedDate
        try:
            commentPatternsMatched["Log Availability Date........"]="From "+logAvailabilityfromtoDate[0]+" To "+logAvailabilityfromtoDate[1]
        except:
            commentPatternsMatched["Log Availability Date........"]="Could not be interpreted from the file : "+commentPatternsMatched["Log Name....................."]
        commentPatternsMatched["logAvstatusDuringFaultDate..."]=logAvstatusDuringFaultDate
        commentPatternsMatched["hansyLink...................."]=hansyLink
        commentPatternsMatched["Serial No...................."]=serialNo
        commentPatternsMatched["Part No......................"]=partNo
        commentPatternsMatched["OverWritten Blocks..........."]=overWrittenBlocks
        commentPatternsMatched["Missing Blocks..............."]=missingBlocks
        if(missedLogSpecificInfo==[]):
            commentPatternsMatched["MissedLogSpecificInfo       :"]="NA"
        else:
            commentPatternsMatched["MissedLogSpecificInfo       :-"]=""
            commentPatternsMatched["    Missed Log Dates    : "]="Missed from "+missedLogSpecificInfo[0][0]+" till "+missedLogSpecificInfo[0][1]
            commentPatternsMatched["    Missed Trace Lines  : "]="\n"+"          "+missedLogSpecificInfo[1][0]+"\n"+"            "+missedLogSpecificInfo[1][1]
        #commentPatternsMatched["suspicious_entries      : "]=suspicious_entries
        return commentPatternsMatched
        
    def getOriginalLogName(self,editedLogName):
        originalLog=editedLogName
        try:
            if(editedLogName.__contains__("_directPro")):
                index_no=editedLogName.index("_directPro")
                if(editedLogName.__contains__("_zipped_bin")):
                    index_no=editedLogName.index("_zipped_bin")
                index_no=index_no-2
                originalLogname=editedLogName[0:index_no]
                logExtension=editedLogName[-4:]
                originalLog=str(originalLogname+logExtension)
                print(originalLog)
        except:
            print("consider checking the file name")
            print(originalLog)
        return originalLog
        
    def deriveCommentParameters(self,commentPatternsMatched,logAvstatusDuringFaultDate,overwritten_info,missing_block_info):
        commentParameters=commentPatternsMatched
        analysisStatement=[]
        whatNext=[]        
        analysisStatement=setAnalysisStatement(logAvstatusDuringFaultDate,overwritten_info,missing_block_info)
        commentParameters["Analysis Statement : "]=analysisStatement
        return commentParameters
        
    def getMatchedTracePatternsList(self,log,logHandler):
        matchedTracePatternInfo=[]
        tracePattern_dict=Global.global_var.g_trace_pattern_config
        faultOccDate=self.faultOccDate
        if self.Component is not None and "SW_SWUPDATE" in self.Component:
            matchedTracePatternInfo=iteratePattern(tracePattern_dict,log,logHandler,faultOccDate,"SW_SWUPDATE")
        else:
            matchedTracePatternInfo=iteratePattern(tracePattern_dict,log,logHandler,faultOccDate)
        if(matchedTracePatternInfo[0]!=[]):
            self.commentParameters["suspicious_entries..........: "]="Matched Trace Patterns listed Below  "
        print(matchedTracePatternInfo)        
        return matchedTracePatternInfo
               
    def frameLogResult(self,commentParametersEvaluated,recommendedComponentsToAnalyze,tracePatternsMatchedList):
        #self.commentParameters
        logResult=""
        tracePatternsMatchedListAsText=""
        heading1="AUTOMATED ANALYSIS UPDATE \n"
        heading2="Below are observations against - "+commentParametersEvaluated["Log Name....................."]+"\n\n" #+" on SW | CustomerVersion :"+
        logResult=heading1+heading2
        for key, value in commentParametersEvaluated.items():
            if(value!="NA"):
                logResult=logResult+"\n"+str(key)+"\t\t"+str(value)+"\n"
        #logResult=logResult+"recommendedComponentsToAnalyze : "+recommendedComponentsToAnalyze+"\n"
        for list_item in tracePatternsMatchedList:
            tracePatternsMatchedListAsText=tracePatternsMatchedListAsText+"\n"+str(list_item)
        logResult=logResult+"\n"+str(tracePatternsMatchedListAsText)
        print("printing log result")
        print(logResult)
        return logResult
        
    def resetLogHandlerToStartOfFile(self,logHandler):
        logHandler.seek(0)
        return logHandler
        
    def closeLogHandler(self,logHandler):
        logHandler.close()
        return
    
    def analyzeDownloadPipe(self,log):
        print("In Analyze Download Pipe")
        print(log)
        #self.commentParameters=[]
        traceParameters=[]               
        logHandler=getLogHandler(log)
        patternsMatched=self.getMatchedPatternsList(log,logHandler)
        if patternsMatched=="":
            patternsMatched="DOWNLOAD PIPE ANALYSIS RESULTS"+"\n"+"No matches found."+"\n"
        else:
            patternsMatched="DOWNLOAD PIPE ANALYSIS RESULTS"+"\n"+patternsMatched
        self.closeLogHandler(logHandler)
        return patternsMatched
    
    def getMatchedPatternsList(self,log,logHandler):
        print("In Matched Patterns")
        matchedPatternInfo=""
        downloadPipePattern_dict=Global.global_var.g_downloadPipe_pattern_config
        print(downloadPipePattern_dict)
        matchedPatternInfo=self.iteratePatterns(downloadPipePattern_dict,log,logHandler)
        print("Matched Patterns")
        print(matchedPatternInfo)
        return matchedPatternInfo
    
    def iteratePatterns(self,downloadPipePattern_dict,log,logHandler):
        print("In Iterate Patterns")
        pattern_count=0
        _listpatternsmatched=""
        print("downloadPipePattern_dict")
        print(downloadPipePattern_dict)
        for downloadPipePattern_pattern in downloadPipePattern_dict:
            stat=False
            print(" In for 1")
            patternstring=str(downloadPipePattern_dict[pattern_count]["PATTERN"])
            print(patternstring)
            logHandler.seek(0)
            patternsmatched=self.checkForPattern(patternstring,logHandler,downloadPipePattern_dict,pattern_count)
            if patternsmatched!="":
                _listpatternsmatched=_listpatternsmatched+patternsmatched
            print(_listpatternsmatched)
            pattern_count=pattern_count+1
        
        print("Download Pipe Pattern")
        print(_listpatternsmatched)
        return _listpatternsmatched

    def checkForPattern(self,patternstring,logHandler,downloadPipePattern_dict,pattern_count):
        _listpatternsmatched=[]
        pipeptrn_string=""
        occur_count=0
        line_count=0
        print("@@@@@@ started checking patterns : ")
        line = logHandler.readline()
        while line:
            line_count=line_count+1
            line_check=str(line)
            match=re.search(patternstring,line_check)
            if match:                
                linenumber=line_count
                #print(tracePattern_dict)
                #print("pattern_matched")
                #print(str(tracePattern_dict[pattern_count]["TRACE_COMMENT"]))
                pipeptrn_string="Line No : "+str(linenumber)+"\n"+str(line)+"\n"+"Pattern Matched : "+str(downloadPipePattern_dict[pattern_count]["COMMENT"])+"\n\n"
                _listpatternsmatched.append(pipeptrn_string)
                occur_count=occur_count+1                          

            line = logHandler.readline()
        print("_listpatternsmatched")
        print(_listpatternsmatched)
        return pipeptrn_string
