#Dashboard_Update -- 
#PTMDT=[TicketNo,label_to_change,logList,analysis_results,result_comment,default_assignee]
#     [TicketNo,label_to_change,logList,analysis_results,result_comment,default_assignee]
#     [TicketNo,label_to_change,logList,analysis_results,result_comment,default_assignee]
import csv
import os
class Dashboard_Updater:
    def __init__(self,PTMDT,METRICS):
        self.PTMDT=PTMDT
        self.METRICS=METRICS
        self.DashBoardDataHeader=["Ticket No","Ticket Status","ARTA_comment","Assignee"]
        self.DashBoardMetricsHeader=["PROCESSED_TICKET_COUNT","SUCCEEEDED_TICKET_COUNT","FAILED_TICKET_COUNT"]
        return
        
    def addFieldsToDataDashBoard(self,header_write):
        with open(r'Errmem_Dashboard.csv', 'a', newline="") as f:
            writer = csv.writer(f)
            if(header_write==1):
                writer.writerow(self.DashBoardDataHeader)
            for PTMD in self.PTMDT:
                DDT=[PTMD[1],PTMD[2],PTMD[5],PTMD[6]]
                writer.writerow(DDT)
        return
        
    def addFieldsToMetricsDashBoard(self,header_write):
        with open(r'Errmem_Metrics.csv', 'a', newline="") as f:
            writer = csv.writer(f)
            if(header_write==1):
                writer.writerow(self.DashBoardMetricsHeader)
            writer.writerow(self.METRICS)
        return
        
    def updateDataDashboard(self):
        header_write=1
        if(os.path.exists("Errmem_Dashboard.csv")):
            header_write=0
        self.addFieldsToDataDashBoard(header_write)        
        return
    
    def updateMetricsDashboard(self):
        header_write=1
        if(os.path.exists("Errmem_Metrics.csv")):
            header_write=0
        self.addFieldsToMetricsDashBoard(header_write)        
        return