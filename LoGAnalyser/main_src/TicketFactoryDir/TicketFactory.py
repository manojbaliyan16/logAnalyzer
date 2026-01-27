class TicketFactory:
    def __init__(self,FTMDT):
        self.FTMDT=FTMDT
        return
    def pickTicket(self,index):
        FTMD=self.FTMDT[index]
        return FTMD