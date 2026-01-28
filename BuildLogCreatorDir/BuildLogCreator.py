import os
import shutil
import datetime
import csv
class BuildLogCreator:
    def __init__(self,buildLogs,date_of_build):
        self.buildLogPath="Error_log.csv"
        self.buildLogHeader=["**BUILD PART**","**ERROR INFO**","**ERROR TYPE**"]
        self.buildLogs=buildLogs
        self.date_of_build=date_of_build
        return
        
    def createBuildLog(self):
        createdStatus=True
        try:
            if(os.path.exists(self.buildLogPath)):
                shutil.rmtree(self.buildLogPath)
        except:
            createdStatus=False
        return createdStatus
        
    def addFieldsToBuildLog(self,header_write,curr_buildLog):
        print(" build log2 ")
        print(curr_buildLog)
        with open(r'Error_log.csv', 'a', newline="") as f:
            writer = csv.writer(f)
            #if(header_write==1):
            writer.writerow([" "," "])
            writer.writerow(["Date of Build : "+self.date_of_build])
            writer.writerow(self.buildLogHeader)
            writer.writerow(curr_buildLog)
        return
        
    def updateBuildLog(self,curr_buildLog):
        header_write=1
        if(os.path.exists(self.buildLogPath)):
            header_write=0
        print(" build log1 ")
        print(curr_buildLog)
        self.addFieldsToBuildLog(header_write,curr_buildLog)        
        return
               
    def writeBuildLog(self):
        try:
            creationStatus=self.createBuildLog()
            for buildLog in self.buildLogs:
                self.updateBuildLog(buildLog)
            writtenStatus=True
        except Exception as e:
            print(e)
            writtenStatus=False
        return writtenStatus
        
        
