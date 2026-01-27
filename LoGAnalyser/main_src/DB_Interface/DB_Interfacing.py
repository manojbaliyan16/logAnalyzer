#from jira import JIRA, JIRAError  # @IgnorePep8
from DB_Interface.JIRA_InitFetchUpdate import *

class DBInterfacing:
    def __init__(self,server,user,password):
        self.server = server
        self.user=user
        self.password=password
        return
        
    #### DB Connection #############
       
    def initializeDB(self):
        DB_reference=[]
        DB_reference=initDB(self.server,self.user,self.password)
        return DB_reference
        
    ######### DB Query Generation ##########
   
    def generateDBQuery(self,ProjectName,Labels_to_process,Component_to_process=None):
        if Component_to_process is None:
            withLabelinList="("
            for label in Labels_to_process:
                if(withLabelinList!="("):
                    withLabelinList=withLabelinList+" OR "
                withLabelinList=withLabelinList+"labels in ("+str(label)
            withLabelinList=withLabelinList+"))"
            DB_query="project ="+ProjectName+" AND "+withLabelinList
            print(DB_query)
            return DB_query 
        else:
            withLabelinList = "(" + ", ".join(Labels_to_process) + ")"

            componentList = "("
            for i, component in enumerate(Component_to_process):
                if i != 0:
                    componentList += " OR "
                componentList += "component = " + str(component)
            componentList += ")"

            DB_query = "project = " + ProjectName + " AND " + "labels in " + withLabelinList + " AND " + componentList
            print(DB_query)
            return DB_query
  

        
    ######### DB Fetch ##########################
    
    def fetchDB(self,DB_query,maxResults,download_path): #connect
        DB_reference=self.initializeDB()
        DB_FTMDT=fetchFTMDT(DB_reference,DB_query,maxResults,download_path)
        return DB_FTMDT
        
    ######### DB Update ##########################
        
    def updateDB(self,DB2_reference,PTMDT_DB):
        DB_reference=self.initializeDB()
        update_status_info={}        
        update_status_info=UpdatePTMDT(DB_reference,PTMDT_DB)
        #update_status_info=UpdateTktParameterstoDB(PTMDT_DB)
        return update_status_info
        
    #### JIRA Disconnection #############
        
    def disconnectDB(self):
        connection_status=True
        return connection_status

    ##################################