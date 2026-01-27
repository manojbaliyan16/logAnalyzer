Labels_to_process=["EMA_Trial","EMA_yy"]
ProjectName="pname"
Component_to_process=[]
'''withLabelinList="("
for label in Labels_to_process:
        if(withLabelinList!="("):
                withLabelinList=withLabelinList+" OR "
        withLabelinList=withLabelinList+"labels in ("+str(label)
withLabelinList=withLabelinList+"))"
DB_query="project ="+ProjectName+" AND "+withLabelinList
print(DB_query)'''

 
withLabelinList = "(" + ", ".join(Labels_to_process) + ")"

componentList = "("
for i, component in enumerate(Component_to_process):
    if i != 0:
        componentList += " OR "
    componentList += "component = " + str(component)
componentList += ")"

DB_query = "project = " + ProjectName + " AND " + "labels in " + withLabelinList + " AND " + componentList
print(DB_query)

