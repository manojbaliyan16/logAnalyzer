import shutil
import os
from configSettings import *
from Global.global_var import *
import zipfile
from zipfile import ZipFile
import subprocess
import re
from pathlib import Path
class Logs:
    def __init__(self,MTMD,tkt_base_folder_path):
        #MTMD--->[status,tkt_number,SW_ID,customerVersion,buildVersion,platform,Relevence,variant,attachmentList,faultDate,TRCPath,Components]     
        self.SW_ID_inJira=MTMD[2]
        self.platform=MTMD[5]
        self.Relevence=MTMD[6]
        self.attachmentPaths=MTMD[8]
        self.TRC_Path=MTMD[10]
        self.Components=MTMD[11]
        self.ComponentsToProcess=Global.global_var.g_feature_control_config["Component to process"]        
        self.tkt_folder_path=tkt_base_folder_path
        return
        
    def getLogs(self):
        attachedproList=[]
        attachedbinList=[]
        attachedziplist=[]
        attachedList=[]
        # New log types
        attacheddltList=[]
        attachedtxtList=[]
        attachedcoredumpList=[]
        proAndBinListInZip=[[],[]]
        validatedProList=[]
        decodedBinList=[]
        LogList=[]
        invalidPros=[]
        invaliddecPros=[]
        renamed_validatedProList=[]
        renamed_decodedBinList=[]
        failed_to_decodeList=[]
        DirectProsFolderPath=""
        DecodedLogsFolderPath=""
        ZippedBinProFolderPath=""
        attachmentPaths=self.attachmentPaths
        print("attachmentPaths")
        print(attachmentPaths)
        for attachment in attachmentPaths:
            attachment=str(attachment)
            if(attachment.endswith(".pro")):
                attachedproList.append(attachment)
            elif(attachment.endswith(".bin")):
                attachedbinList.append(attachment)
            elif(attachment.endswith(".zip")):
                attachedziplist.append(attachment)
            elif(attachment.endswith(".dlt")):
                attacheddltList.append(attachment)
            elif(attachment.endswith(".txt")):
                attachedtxtList.append(attachment)
            elif(attachment.endswith((".core", ".dump", ".dmp", ".backtrace"))):
                attachedcoredumpList.append(attachment)
            elif("downloadPipe" in attachment):
                attachedList.append(attachment)
        if(attachedziplist!=[]):            
            DownloadedZipsFolderPath=os.path.join(self.tkt_folder_path, "Downloaded_ZIPS")
            self.createLOGSFolder(DownloadedZipsFolderPath)
            print("attachedziplist")
            print(attachedziplist)
            self.copyFiles(attachedziplist,DownloadedZipsFolderPath)
            proAndBinListInZip=self.checkforProOrBinInZipFiles(DownloadedZipsFolderPath)
            attachedproList=attachedproList+proAndBinListInZip[0]
            attachedbinList=attachedbinList+proAndBinListInZip[1]
            attachedList=attachedList+proAndBinListInZip[2]
            if((self.TRC_Path=="Undetermined")or(self.TRC_Path=="Empty")):
                failed_to_decodeList=attachedbinList                
                attachedbinList=[]
        if(attachedproList!=[]):
            print("attachedproList")
            print(attachedproList)
            validatedProList=self.validateDirectPro(attachedproList,self.SW_ID_inJira)
            validPros=validatedProList[0]
            invalidPros=validatedProList[1]
            if(validPros!=[]):
                print("validatedProList1 -- ")
                print(validatedProList)
                renamed_validatedProList=self.renameFiles(validPros,"directPro")
                DirectProsFolderPath=os.path.join(self.tkt_folder_path, "DirectPro_LOGS")
                self.createLOGSFolder(DirectProsFolderPath)
                self.copyFiles(renamed_validatedProList,DirectProsFolderPath)
                #self.deleteFilesIfExists(renamed_validatedProList)
        if(attachedbinList!=[]):
            print("self.TRC_Path")
            print(self.TRC_Path)
            if((self.TRC_Path!="Undetermined")and(self.TRC_Path!="Empty")):               
                DecodedLogsFolderPath=os.path.join(self.tkt_folder_path, "Decoded_LOGS")
                self.createLOGSFolder(DecodedLogsFolderPath)
                extensionChangedBinList=self.changeExtension(attachedbinList,".pro")
                decodedBinList=self.decodeBin(extensionChangedBinList,DownloadedZipsFolderPath,DecodedLogsFolderPath)
                if(decodedBinList!=[]):
                    validateddecProList=[[],[]]
                    invaliddecPros=[]
                    validateddecProList=self.validateDirectPro(renamed_decodedBinList,self.SW_ID_inJira)
                    if(validateddecProList!=[[],[]]):
                        print("validateddecProList -- ")
                        print(validateddecProList)
                        renamed_decodedBinList=self.renameFiles(validateddecProList[0]+validateddecProList[1],"decoded_auto")                    
                        print("renamed_decodedBinList")
                        print(validateddecProList)
                        self.copyFiles(validateddecProList[0],DecodedLogsFolderPath)
                        invaliddecPros=validateddecProList[1]
                        print("invaliddecPros")
                        print(invaliddecPros)
                        renamed_decodedBinList=validateddecProList[0]
                #self.deleteFilesIfExists(renamed_decodedBinList)
        
        # Process DLT files
        if(attacheddltList!=[]):
            print("Processing DLT files...")
            print(attacheddltList)
            processed_dlt = self.processDLTFiles(attacheddltList)
            renamed_validatedProList.extend(processed_dlt)
        
        # Process TXT files
        if(attachedtxtList!=[]):
            print("Processing TXT files...")
            print(attachedtxtList)
            processed_txt = self.processTextFiles(attachedtxtList)
            renamed_validatedProList.extend(processed_txt)
        
        # Process Coredump files
        if(attachedcoredumpList!=[]):
            print("Processing Coredump/Backtrace files...")
            print(attachedcoredumpList)
            processed_coredumps = self.processCoredumps(attachedcoredumpList)
            renamed_validatedProList.extend(processed_coredumps)
        
        validLogList=renamed_validatedProList+renamed_decodedBinList+failed_to_decodeList
        LogList=[validLogList,invalidPros+invaliddecPros,attachedList]
        print("LogList -Logs")
        print(LogList)
        return LogList
        
    def checkforProOrBinInZipFiles(self,DownloadedZipsFolderPath):
        proAndBinListInZip=[[],[]]
        renamedproAndBinListInZip=[[],[],[]]
        temprenamedproAndBinListInZip=[[],[]]
        zipContents=[]
        rawzipFilePathList=[]
        extractedprofilePath=""
        extractedbinfilePath=""
        extractedfilePath=""
        for root,dir,files in os.walk(DownloadedZipsFolderPath):
            for file in files:
                if file.endswith(".zip"):
                    print("zipped file detected")
                    print(file)
                    rawzipFilePath=os.path.join(DownloadedZipsFolderPath,file)
                    rawzipFilePathList.append(rawzipFilePath)
                    filename,extension = os.path.splitext(file)            
                    extractedzipFolder=DownloadedZipsFolderPath+str(filename)+"\\"
                    zipNameToConcatenate=str(filename)
                    zipNameToConcatenate=zipNameToConcatenate[0:12]
                    zipfileToExtractPath=DownloadedZipsFolderPath+str(file)
                    self.createLOGSFolder(extractedzipFolder)
                    print("extractedzipFolder")
                    print(extractedzipFolder)
                    with ZipFile(zipfileToExtractPath,'r') as zipObj:
                        zipObj.extractall(extractedzipFolder)
                    for extracted_file in os.listdir(extractedzipFolder):
                        if(extracted_file.endswith(".pro")):                            
                            print("extractedprofilePath")
                            print(extractedprofilePath)
                            extractedprofilePath=os.path.join(extractedzipFolder,extracted_file)
                            proAndBinListInZip[0].append(extractedprofilePath)
                        elif(extracted_file.endswith(".bin")):
                            extractedbinfilePath=os.path.join(extractedzipFolder,extracted_file)
                            proAndBinListInZip[1].append(extractedbinfilePath)
                        elif(extracted_file.find("downloadPipe")):
                            extractedfilePath=os.path.join(extractedzipFolder,extracted_file)
                            renamedproAndBinListInZip[2].append(extractedfilePath)
                    print("proAndBinListInZip")
                    print(proAndBinListInZip)
                    if(proAndBinListInZip[0]!=[]):
                        temprenamedproAndBinListInZip[0]=self.renameFiles(proAndBinListInZip[0],zipNameToConcatenate+"_zipped_directPro")
                    if(proAndBinListInZip[1]!=[]):
                        temprenamedproAndBinListInZip[1]=self.renameFiles(proAndBinListInZip[1],"zipped_bin")
                    proAndBinListInZip=[[],[]]
                    renamedproAndBinListInZip[0]=renamedproAndBinListInZip[0]+temprenamedproAndBinListInZip[0]
                    renamedproAndBinListInZip[1]=renamedproAndBinListInZip[1]+temprenamedproAndBinListInZip[1]
        #self.deleteFiles(rawzipFilePathList)
        return renamedproAndBinListInZip       
         
    def validateDirectPro(self,attachedproList,SW_ID_inJira):
        validatedProList=[[],[]]
        validPros=[]
        invalidPros=[]
        for attachedpro in attachedproList:
            handler=self.getAttachmentHandler(attachedpro)
            line = handler.readline()
            print(str(line))
            if self.Components is not None:
                validPros.append(attachedpro)
            else:                
                try:
                    while line:
                        line_check=str(line)
                        #swid_str=_SW_ID
                        SW_ID_pattern_strings=["<file@card>OSALCORE  \"AI_PRJ_RN_AIVI_","<gen3flex@dlt>(core0)OSALCORE  \"AI_PRJ_RN_AIVI_"]
                        #SW_ID_pattern_strings=Global.global_var.g_validation_pattern_config["_SW_ID_inFile"]
                        if(SW_ID_pattern_strings[0] in line_check) or (SW_ID_pattern_strings[1] in line_check):
                            swid=re.findall('"([^"]*)"', line_check)
                            swid_str=str(swid[0])
                            if(swid_str!=SW_ID_inJira):
                                self.SW_ID_inJira=swid_str
                            validPros.append(attachedpro)
                            break
                        line = handler.readline()#handler.close()
                except Exception as e:
                    print(str(e))
                    print("Error in parsing the file :"+str(attachedpro))
                
            handler.close()
            set_dif = set(attachedproList).symmetric_difference(set(validPros))
            diffPros = list(set_dif)
            """
            for proFile in diffPros:
                if(".pro" in proFile):
                    proFile.replace(".pro","invalid.pro")
                    invalidPros.append(proFile)
            """
        validatedProList[0]=validPros
        validatedProList[1]=invalidPros
        print("validatedProList")
        print(validatedProList)
        return validatedProList
        
    def createLOGSFolder(self,folder_path):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        return
        
    def  decodeBin(self,attachedbinList,DownloadedZipsFolderPath,DecodedLogsFolderPath):
        specific_TRC_Path=self.getSpecificTRCPath(self.TRC_Path,self.Relevence,self.platform)
        runArgumentsDecoderList=[]
        decodedBinList=[]
        DecoderPath=Global.global_var.g_feature_control_config["DecoderPath"]
        for attachedbin in attachedbinList:
            runArgumentsDecoderList=[DecoderPath,"--trcFile="+str(specific_TRC_Path),"--in="+str(attachedbin)]
            print("specific_TRC_Path")
            print(specific_TRC_Path)
            getDecodedFile=subprocess.Popen(runArgumentsDecoderList)
            print("Decoding in progress")
            status=getDecodedFile.wait()
            print("Decoding completed")
        binplacedFolder=self.tkt_folder_path
        for file in os.listdir(binplacedFolder):
            if(str(file).endswith("decoded.pro")):
              dirfilepath=str(self.tkt_folder_path)+"\\"+str(file)  
              decodedBinList.append(dirfilepath)
        # for files in downloaded zip
        binplacedFolder=DownloadedZipsFolderPath
        for direc in os.scandir(binplacedFolder):
            if direc.is_dir():
                for file in os.listdir(direc):
                    if file.endswith("decoded.pro"):
                        direcLocation=direc.path
                        decodedBinFilePath=direcLocation+"\\"+str(file)
                        decodedBinList.append(decodedBinFilePath)
        print("decodedBinList")
        print(decodedBinList)
        return decodedBinList
        
    def copyFiles(self,source_files_paths,destn_folder_path):
        for source_file_path in source_files_paths:
            print("source_file_path")
            print(source_file_path)
            shutil.copy(source_file_path,destn_folder_path)
        return
    
    def renameFiles(self,files_pathList,suffixText):
        renamedfiles_pathList=[]
        suffix_name=""
        index_number=1
        for filePath in files_pathList:
            index_string=str(index_number)
            filename,extension = os.path.splitext(filePath)
            suffix_name="_"+index_string+"_"+str(suffixText)
            renamedfile_path=filename+suffix_name+extension
            os.rename(filePath,renamedfile_path)
            print("filePath")
            print(filePath)
            print("renamedfile_path")
            print(renamedfile_path)
            renamedfiles_pathList.append(renamedfile_path)
            index_number=index_number+1
        return renamedfiles_pathList
        
    def getAttachmentHandler(self,attachment_path):
        attachmentHandler="Invalid File"
        try:
            attachmentHandler=open(attachment_path,encoding="utf8",errors='ignore')
        except:
            try:
                attachmentHandler=open(attachment_path,encoding="latin-1",errors='ignore')
            except:
                attachmentHandler=open(attachment_path,encoding="ISO-8859-1",errors='ignore')
        return attachmentHandler
        
    def getSpecificTRCPath(self,TRC_Path,Relevence,platform):
        SpecificTRCPath=""
        #currentTicketFolder=str(self.tkt_folder_path)
        if(platform=="gen4"):
            SpecificTRCPath=TRC_Path+"\\"+"prj_overall_accumulated_rcar_release.trc"
        elif(Relevence=="P-IVI"):
            jira_SWID=str(self.SW_ID_inJira)
            if("AI_PRJ_RN_AIVI_18" in jira_SWID):
                SpecificTRCPath=TRC_Path
                print("For Common release version of PIVI with scope 2.1 -- taking all the trc files for decoding")
        else:
            SpecificTRCPath=TRC_Path+"\\"+"prj_overall_accumulated_arm_release.trc"
        return SpecificTRCPath
        
    def deleteFiles(self,FilesPathsList):
        for FilePath in FilesPathsList:
            if(os.path.exists(FilePath)):
                shutil.rmtree(FilePath)
        return
    def changeExtension(self,attachedbinList,extension_toChange):
        extensionChangedBinList=[]
        for attachedbin in attachedbinList:
            #attachedbinName=Path(attachedbin).name
            binfile=os.path.basename(attachedbin)
            binlocation = os.path.dirname(attachedbin)
            if(binfile.endswith(".bin")):
                binname=binfile[:-4]
                print("binname")
                print(binname)
                changedProName=binname+extension_toChange
                changedProLocationpath=os.path.join(binlocation, changedProName)
                print("changedProLocationpath")
                print(changedProLocationpath)
                os.rename(attachedbin,changedProLocationpath)               
                extensionChangedBinList.append(changedProLocationpath)
        return extensionChangedBinList
    
    def processDLTFiles(self, dlt_files):
        """Process .dlt files and convert to analyzable format"""
        from LogsDir.LogTypeHandlers import DLTLogHandler
        
        processed_files = []
        DLTLogsFolderPath = os.path.join(self.tkt_folder_path, "DLT_LOGS")
        self.createLOGSFolder(DLTLogsFolderPath)
        
        for dlt_file in dlt_files:
            try:
                print(f"Processing DLT file: {dlt_file}")
                handler = DLTLogHandler(dlt_file)
                
                # Validate DLT file
                is_valid, msg = handler.validate()
                if not is_valid:
                    print(f"Invalid DLT file {dlt_file}: {msg}")
                    continue
                
                # Convert to text format
                text_log = handler.extract_traces()
                
                # Copy converted file to DLT logs folder
                dest_path = os.path.join(DLTLogsFolderPath, os.path.basename(text_log))
                shutil.copy2(text_log, dest_path)
                processed_files.append(dest_path)
                print(f"✓ Successfully processed DLT file: {os.path.basename(dlt_file)}")
                
            except Exception as e:
                print(f"Error processing DLT file {dlt_file}: {e}")
                continue
        
        return processed_files
    
    def processTextFiles(self, txt_files):
        """Process .txt log files"""
        from LogsDir.LogTypeHandlers import TextLogHandler
        
        processed_files = []
        TextLogsFolderPath = os.path.join(self.tkt_folder_path, "TEXT_LOGS")
        self.createLOGSFolder(TextLogsFolderPath)
        
        for txt_file in txt_files:
            try:
                print(f"Processing TXT file: {txt_file}")
                handler = TextLogHandler(txt_file)
                
                # Validate text file
                is_valid, msg = handler.validate_format()
                if not is_valid:
                    print(f"Invalid TXT file {txt_file}: {msg}")
                    continue
                
                # Normalize encoding if needed
                normalized_file = handler.normalize_encoding(
                    os.path.join(TextLogsFolderPath, os.path.basename(txt_file))
                )
                processed_files.append(normalized_file)
                print(f"✓ Successfully processed TXT file: {os.path.basename(txt_file)}")
                
            except Exception as e:
                print(f"Error processing TXT file {txt_file}: {e}")
                # If normalization fails, try to use original file
                try:
                    dest_path = os.path.join(TextLogsFolderPath, os.path.basename(txt_file))
                    shutil.copy2(txt_file, dest_path)
                    processed_files.append(dest_path)
                except:
                    continue
        
        return processed_files
    
    def processCoredumps(self, coredump_files):
        """Process coredump files and extract backtraces"""
        from LogsDir.LogTypeHandlers import CoredumpHandler
        
        processed_files = []
        CoredumpLogsFolderPath = os.path.join(self.tkt_folder_path, "COREDUMP_LOGS")
        self.createLOGSFolder(CoredumpLogsFolderPath)
        
        for core_file in coredump_files:
            try:
                print(f"Processing Coredump file: {core_file}")
                handler = CoredumpHandler(core_file)
                
                # Validate coredump file
                is_valid, msg = handler.validate()
                if not is_valid:
                    print(f"Invalid Coredump file {core_file}: {msg}")
                    continue
                
                # Extract backtrace
                backtrace_file = handler.analyze_crash()
                
                # Copy backtrace to coredump logs folder
                dest_path = os.path.join(CoredumpLogsFolderPath, os.path.basename(backtrace_file))
                shutil.copy2(backtrace_file, dest_path)
                processed_files.append(dest_path)
                print(f"✓ Successfully processed Coredump: {os.path.basename(core_file)}")
                
            except Exception as e:
                print(f"Error processing Coredump {core_file}: {e}")
                print("Note: Ensure GDB (Linux) or CDB (Windows) is installed for coredump analysis")
                continue
        
        return processed_files