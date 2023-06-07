import sqlite3, plotly.express as px, pandas as pd, copy
import plotly.io as pio
pio.renderers.default = "browser"
#pio.renderers.default = "notebook_connected"

mpecconn = sqlite3.connect("..\\mpec_files\\mpecwatch_v3.db")
cursor = mpecconn.cursor()

def printDict(someDictionary):
    for key,value in someDictionary.items():
        print("{}: {}".format(key,value))

def tableNames():
    sql = '''SELECT name FROM sqlite_master WHERE type='table';'''
    cursor = mpecconn.execute(sql)
    results = cursor.fetchall()
    return(results[1::])

#creating and writing Pie chart to html
def topN(someDictionary, graphTitle, station, includeNA = False):
    allObjects = dict(sorted(someDictionary.items(), key=lambda x:x[1], reverse = True))
    
    if includeNA:
        titleNA = "+NA"
        if '' in allObjects:     #check observation type
            allObjects['N/A'] = allObjects['']
            del allObjects['']
    else:
        titleNA=""
        if '' in allObjects:
            del allObjects['']

    if 0 in allObjects:
        del allObjects[0]
    
    if len(allObjects) > N: #if more than N data points DO top 10 + other
        topObjects = dict(sorted(allObjects.items(), key=lambda x:x[1], reverse = True)[:N])
        topObjects.update({"Others":sum(allObjects.values())-sum(topObjects.values())})
    else: #otherwise show all data points
        topObjects = dict(sorted(allObjects.items(), key=lambda x:x[1], reverse = True))    
    
    #printDict(topObjects)
    df = pd.DataFrame(list(topObjects.items()), columns=['Objects', 'Count'])
    #print(df)
    fig1 = px.pie(df, values='Count', names='Objects', title=station + " | " + graphTitle)
    fig1.write_html("..\\mpec_files\\OMF\\"+station+"_"+graphTitle+"{}.html".format(titleNA))
    #fig1.show()
    print(station)

N = 10 #Top limit of objects to show individually
for station in tableNames():
    observers = {}
    measurers = {}
    facilities = {}
    cursor.execute("select * from {}".format(station[0]))
    observations = cursor.fetchall()
    for observation in observations:
        observers[observation[2]] = observers.get(observation[2],0)+1
        measurers[observation[3]] = measurers.get(observation[3],0)+1
        facilities[observation[4]] = facilities.get(observation[4],0)+1
    
    
    topN(observers, "Top_{}_Observers".format(N), station[0])
    topN(measurers, "Top_{}_Measurers".format(N), station[0])
    #includes NA:
    #topN(measurers, "Top {} Measurers".format(N), station[0], True)
    topN(facilities, "Top_{}_Facilities".format(N), station[0])
    
    #includes NA
    #topN(observers, "Top {} Observers".format(N), station[0], True)
    
mpecconn.close()
print('finished')
    