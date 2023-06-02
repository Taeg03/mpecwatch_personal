# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 14:49:19 2022

(a) Bar chart + break-down table of the number and type of MPECs by year (like the one on the home page)

Database structure
---
    Key            Type        Description
TABLE MPEC: (summary of each MPEC)
    0 MPECId        TEXT        MPEC Number
    1 Title        TEXT        MPEC Title
    2 Time        INTEGER      Publication Unix timestamp
    3 Station        TEXT        List of observatory stations involved in the observation. Only used when MPECType is Discovery, OrbitUpdate, or DOU        
    4 DiscStation    TEXT        Observatory station marked by the discovery asterisk. Only used when MPECType is Discovery.
    5 FirstConf    TEXT        First observatory station to confirm. Only used when MPECType is Discovery.
    6 MPECType    TEXT        Type of the MPEC: Editorial, Discovery, OrbitUpdate, DOU, ListUpdate, Retraction, Other
    7 ObjectType    TEXT        Type of the object: NEA, Comet, Satellite, TNO, Unusual, Interstellar, unk. Only used when MPECType is Discovery or OrbitUpdate
    8 OrbitComp    TEXT        Orbit computer. Only used when MPECType is Discovery or OrbitUpdate
    9 Issuer        TEXT        Issuer of the MPEC
    
TABLE station_XXX (observatory code):
    0 Object        TEXT        Object designation in packed form
    1 Time        INTEGER        Time of the observation (Unix timestamp)
    2 Observer    TEXT        List of observers as published in MPEC
    3 Measurer    TEXT        List of measurers as published in MPEC
    4 Facility    TEXT        List of telescope/instrument as published in MPEC
    5 MPEC        TEXT        MPECId1
    6 MPECType    TEXT        Type of the MPEC: Discovery, OrbitUpdate, DOU
    7 ObjectType    TEXT        Type of the object: NEA, Comet, Satellite, TNO, Unusual, Interstellar, unk
    8 Discovery    INTEGER        Corresponding to discovery asterisk
"""

import sqlite3, pandas as pd, plotly.express as px, datetime, numpy as np, copy
from datetime import date

mpecconn = sqlite3.connect("C:\\Users\\taega\\Documents\\mpec_files\\mpecwatch_v3.db")
cursor = mpecconn.cursor()

#prints the contents of a table w/ output limit
def printTableContent(table):
    rows = cursor.execute("SELECT * FROM {} WHERE Object = 'J99M00L' LIMIT 100".format(table)).fetchall()
    print(rows)
def tableNames():
    sql = '''SELECT name FROM sqlite_master WHERE type='table';'''
    cursor = mpecconn.execute(sql)
    results = cursor.fetchall()
    return(results[1::])
def printDict(someDictionary):
    for key,value in someDictionary.items():
        print("{}: {}".format(key,value))

BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
def encode(num, alphabet=BASE62):
    """Encode a positive number in Base X
    Arguments:
    - `num`: The number to encode
    - `alphabet`: The alphabet to use for encoding
    """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def calcObs():
    d = dict()
    cursor.execute("select * from MPEC")
    for mpec in cursor.fetchall():
        year = date.fromtimestamp(mpec[2]).year
        for station in mpec[3].split(', '):
            if station == "":
                continue

            if station not in d:
                d[station] = {}
                d[station]['Followup'] = {}
                d[station]['FirstFollowup'] = {}
                d[station]['Discovery'] = {}
                d[station]['Editorial'] = {}
                d[station]['OrbitUpdate'] = {}
                d[station]['DOU'] = {}
                d[station]['ListUpdate'] = {}
                d[station]['Retraction'] = {}
                d[station]['Other'] = {}
                d[station]['MPECs'] = []

            #MPECType = 'Discovery' and DiscStation != '{}'
            if mpec[6] == 'Discovery' and station != mpec[4]:
                try:
                    #attempts to increment dict value by 1
                    d[station]['Followup'][year] = d[station]['Followup'].get(year,0)+1
                except:
                    #creates dict key and adds 1
                    d[station]['Followup'][year] = 1

            #MPECType = 'Discovery' and DiscStation != '{}' and "disc_station, station" in stations
            if mpec[6] == 'Discovery' and station not in mpec[4] and mpec[4] + ', ' + station in mpec[3]:
                try:
                    d[station]['FirstFollowup'][year] = d[station]['FirstFollowup'].get(year,0)+1
                except:
                    d[station]['FirstFollowup'][year] = 1

            #if station = discovery station
            if station == mpec[4]:
                try:
                    d[station]['Discovery'][year] = d[station]['Discovery'].get(year,0)+1
                except:
                    d[station]['Discovery'][year] = 1
            
            for mpecType in ["Editorial", "OrbitUpdate", "DOU", "ListUpdate", "Retraction", "Other"]:
                if mpec[6] == mpecType:
                    try:
                        #attempts to increment dict value by 1
                        d[station][mpecType][year] = d[station][mpecType].get(year,0)+1
                    except:
                        #creates dict key and adds 1
                        d[station][mpecType][year] = 1

            #listing all the MPECs from one station: USING TITLE (from MPEC table)
            temp = []
            name = mpec[0] + "\t" + mpec[1]
            if name not in d[station]['MPECs']: #prevents duplication of the same MPEC object
                temp.append(name) #
                temp.append(datetime.datetime.fromtimestamp(mpec[2])) #time: date and time
                #if station = discovery station
                if station == mpec[4]:
                    temp.append("&#x2713") #check mark
                else:
                    temp.append("")
                #if station = FirstFU
                if station == mpec[5]:
                    temp.append("&#x2713") #check mark
                else:
                    temp.append("")
                
                obj_type = mpec[7]
                temp.append(obj_type)
                id = mpec[0][5::]
                packed_front = ""
                packed_back = ""

                #packed front
                if id[0:2] == "18":
                    packed_front = "I" + id[2:4]
                elif id[0:2] == "19":
                    packed_front = "J" + id[2:4]
                elif id[0:2] == "20":
                    packed_front = "K" + id[2:4]
                    
                #packed_back
                if len(id) == 8:
                    packed_back = packed_front + id[-3::]
                elif len(id) == 9:
                    packed_back = packed_front + id[5] + encode(int(id[6:8])) + id[-1]
                
                url1 = "\"https://www.minorplanetcenter.net/mpec/{}/{}.html\"".format(packed_front, packed_back)
                mpec_url = "<a href={}>Details</a>".format(url1)
                temp.append(mpec_url)
                d[station]['MPECs'].append((temp))
    return d
    
def main():
    mpec_data = calcObs()
    includeFirstFU = True
    #for station_name in tableNames():
    for station_name in range(1):
        df = pd.DataFrame({"Year": [], "MPECType": [], "#MPECs": []})
        #station = station_name[0]
        station = 'station_J95'
        #print(mpec_data[station[-3::]]['MPECs'])
        ''' Prints the MPECs for each station
        for MPEC in mpec_data[station[-3::]]['MPECs']:
            print(MPEC)
        '''
        page = "C:\\Users\\taega\\Documents\\mpec_files\\WEB_Stations\\WEB_" + str(station) + ".html"
        o = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        <link href="https://unpkg.com/bootstrap-table@1.21.4/dist/bootstrap-table.min.css" rel="stylesheet">

        <script src="https://unpkg.com/bootstrap-table@1.21.4/dist/bootstrap-table.min.js"></script>
        <title>{}</title>
    </head>
    <body>
        <div class="container">
            <div>
              <h3>Graph 1</h3>
              <p>
                  Graph Supported by Plotly
                  <iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="C:\\Users\\taega\\Documents\\mpec_files\\WEB_Stations\\Graphs\\{}.html" height="525" width="100%"></iframe>
              </p>
            </div>
            <table class="table table-striped table-sm">
                <tr>
                    <th>Year</th>
                    <th>Total MPECs</th>
                    <th>Editorial</th>
                    <th>Discovery</th>
                    <th>P/R/FU</th>
                    <th>DOU</th>
                    <th>List Update</th>
                    <th>Retraction</th>
                    <th>Other</th>
                    <th>Follow-Up</th>
                    <th>First Follow-Up</th>
                </tr>
        """.format(station.capitalize(), station)
        
        for year in list(np.arange(1993, datetime.datetime.now().year+1, 1))[::-1]:
            obs_types = ["Editorial", "Discovery", "OrbitUpdate", "DOU", "ListUpdate", "Retraction", "Other", "Followup", "FirstFollowup"]
            mpec_counts = list(map(lambda func: func(), [lambda mpecType=x: mpec_data[station[8::]][mpecType][year] if year in mpec_data[station[8::]][mpecType].keys() else 0 for x in obs_types]))
            if includeFirstFU:
                mpec_counts[7] -= mpec_counts[8]
            else:
                mpec_counts[8] = 0
            
            df = pd.concat([df, pd.DataFrame({"Year": [year, year, year, year, year, year, year, year, year], "MPECType": ["Editorial", "Discovery", "OrbitUpdate", "DOU", "ListUpdate", "Retraction", "Other", "Followup", "FirstFollowup"], "#MPECs": mpec_counts})])

            o += """
                <tr>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                    <td>%i</td>
                </tr>
            """ % (year, sum(mpec_counts), mpec_counts[0], mpec_counts[1], mpec_counts[2], mpec_counts[3], mpec_counts[4], mpec_counts[5], mpec_counts[6], mpec_counts[7], mpec_counts[8])

        o += """
            </table>
        </div>
        <div class="container">
            <table id="table" 
                class="table table-striped table-bordered table-sm"
                data-toggle="table"
                data-height="460"
                data-pagination="true">
                <thead>
                    <tr>
                        <th class="th-sm" data-field="name">Name

                        </th>
                        <th class="th-sm" data-field="date">Date/Time

                        </th>
                        <th class="th-sm" data-field="ds">DiscStation

                        </th>
                        <th class="th-sm" data-field="fs">FirstConf

                        </th>
                        <th class="th-sm" data-field="obj">Object

                        </th>
                        <th class="th-sm" data-field="url">URL

                        </th>
                    </tr>
                </thead>
                <tbody>
        """
        for i in mpec_data[station[-3::]]['MPECs']:
            o += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
            """.format(i[0],i[1],i[2],i[3],i[4],i[5])
        
        fig = px.bar(df, x="Year", y="#MPECs", color="MPECType", title= station.capitalize()+" | Number and type of MPECs by year")
        fig.write_html("C:\\Users\\taega\\Documents\\mpec_files\\WEB_Stations\\Graphs\\{}.html".format(station))
        o += """    
                </tbody>
            </table>
            <script src="https://cdn.jsdelivr.net/npm/jquery/dist/jquery.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
            <script src="https://unpkg.com/bootstrap-table@1.21.4/dist/bootstrap-table.min.js"></script>
        </div>
    </body>
</html>"""
        print(station)
        with open(page, 'w') as f:
            f.write(o)

'''
start = time.perf_counter()
main()
finish = time.perf_counter()
print('Time: ', finish-start)
'''

main()
mpecconn.close()
print('finished')