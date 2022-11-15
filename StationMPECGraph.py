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
    
TABLE XXX (observatory code):
    0 Object        TEXT        Object designation in packed form
    1 Time        INTEGER        Time of the observation (Unix timestamp)
    2 Observer    TEXT        List of observers as published in MPEC
    3 Measurer    TEXT        List of measurers as published in MPEC
    4 Facility    TEXT        List of telescope/instrument as published in MPEC
    5 MPEC        TEXT        MPECId
    6 MPECType    TEXT        Type of the MPEC: Discovery, OrbitUpdate, DOU
    7 ObjectType    TEXT        Type of the object: NEA, Comet, Satellite, TNO, Unusual, Interstellar, unk
    8 Discovery    INTEGER        Corresponding to discovery asterisk
"""

import sqlite3, plotly.express as px, pandas as pd, datetime, numpy as np
import time, calendar, re
from datetime import date
from collections import defaultdict

mpecconn = sqlite3.connect("C:\\Users\\taega\\OneDrive\\Documents\\mpec_files\\mpecwatch_v3.db")
cursor = mpecconn.cursor()
currentYear = datetime.datetime.now().year

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

d = dict()
def calcObs():
    cursor.execute("select * from MPEC")
    for mpec in cursor.fetchall():
        year = date.fromtimestamp(mpec[2]).year
        for station in mpec[3].split(', '):
            if station not in d:
                d[station] = {}
                d[station]['mpec_followup'] = {}
                d[station]['mpec_1st_followup'] = {}
            #MPECType = 'Discovery' and DiscStation != '{}'
            if mpec[6] == 'Discovery' and station != mpec[4]:
                try:
                    #attempts to increment dict value by 1
                    d[station]['mpec_followup'][year] = d[station]['mpec_followup'].get(year,0)+1
                except:
                    #creates dict key and adds 1
                    d[station]['mpec_followup'][year] = 1

            #MPECType = 'Discovery' and DiscStation != '{}' and "disc_station, station" in stations
            if mpec[6] == 'Discovery' and station not in mpec[4] and mpec[4] + ', ' + station in mpec[3]:
                try:
                    d[station]['mpec_1st_followup'][year] = d[station]['mpec_1st_followup'].get(year,0)+1
                except:
                    d[station]['mpec_1st_followup'][year] = 1

            for mpecType in ["Editorial", "OrbitUpdate", "DOU", "ListUpdate", "Retraction", "Other"]:
                if mpec[6] == mpecType:
                    try:
                        #attempts to increment dict value by 1
                        d[station][mpecType][year] = d[station][mpecType].get(year,0)+1
                    except:
                        #creates dict key and adds 1
                        d[station][mpecType][year] = 1
            
def main():
    calcObs()
    includeFirstFU = True
    blankStations = []
    #for station_name in tableNames():
    for station_name in range(1):
        FUcount = 0
        F_FUcount = 0
        totalMPEC = 0
        df = pd.DataFrame({"Year": [], "MPECType": [], "#MPECs": []})
        #station = station_name[0]
        station = 'station_J95'
        editorials = set()
        discoveries = set()
        orbitupdates = set()
        dous = set()
        listupdates = set()
        retractions = set()
        others = set()
        page = "C:\\Users\\taega\\OneDrive\\Documents\\mpec_files\\WEB_Stations\\WEB_" + str(station) + ".html"
        o = """
        <div class="jumbotron text-center">
          <h1>{}</h1>
          <p>Graphs supported by Plotly</p>
        </div>
        
        <div class="container">
          <div class="row">
            <div class="col-sm-4">
              <h3>Graph 1</h3>
              <p>
                  Testing
                  <iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="C:\\Users\\taega\\OneDrive\\Documents\\mpec_files\\WEB_Stations\\Graphs\\{}.html" height="525" width="100%"></iframe>
              </p>
            </div>
            <table>
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
                    <th>1st follow-up</th>
                </tr>
            </table>
        """.format(station.capitalize(), station)
        
        
        for year in list(np.arange(1993, datetime.datetime.now().year+1, 1))[::-1]:
            '''year_start = datetime.datetime(year, 1, 1, 0, 0, 0).timestamp()
            year_end = datetime.datetime(year, 12, 31, 23, 59, 59).timestamp()
            cursor.execute("select * from {} where Time >= {} and Time <= {} and MPECType = '{}'".format(station, year_start, year_end, 'Editorial'))
            for i in cursor.fetchall():
                editorials.add(i[5])
            editorial = len(editorials)
            cursor.execute("select * from {} where Time >= {} and Time <= {} and Discovery == 1".format(station, year_start, year_end))
            for i in cursor.fetchall():
                discoveries.add(i[5])
            discovery = len(discoveries)
            cursor.execute("select * from {} where Time >= {} and Time <= {} and MPECType = '{}'".format(station, year_start, year_end, 'OrbitUpdate'))
            for i in cursor.fetchall():
                orbitupdates.add(i[5])
            orbitupdate = len(orbitupdates)
            cursor.execute("select * from {} where Time >= {} and Time <= {} and MPECType = '{}'".format(station, year_start, year_end, 'DOU'))
            for i in cursor.fetchall():
                dous.add(i[5])
            dou = len(dous)
            cursor.execute("select * from {} where Time >= {} and Time <= {} and MPECType = '{}'".format(station, year_start, year_end, 'ListUpdate'))
            for i in cursor.fetchall():
                listupdates.add(i[5])
            listupdate = len(listupdates)
            cursor.execute("select * from {} where Time >= {} and Time <= {} and MPECType = '{}'".format(station, year_start, year_end, 'Retraction'))
            for i in cursor.fetchall():
                retractions.add(i[5])
            retraction = len(retractions)
            cursor.execute("select * from {} where Time >= {} and Time <= {} and MPECType = '{}'".format(station, year_start, year_end, 'Other'))
            for i in cursor.fetchall():
                others.add(i[5])
            other = len(others)'''
            #print(test_dict[station[8::]]['mpec_followup'][int(year)])
            #print(test_dict[station[8::]]['mpec_1st_followup'][int(year)])
            
            array = ["Editorial", "Discovery", "OrbitUpdate", "DOU", "ListUpdate", "Retraction", "Other", "mpec_followup", "mpec_1st_followup"]
            mpec_counts = [lambda mpecType=x: d[station[8::]][mpecType][year] if year in d[station[8::]][mpecType].keys() else 0 for x in array]
            if includeFirstFU:
                mpec_counts[7] -= mpec_counts[8]
            else:
                mpec_counts[8] = 0
            
            df = df.append(pd.DataFrame({"Year": [year, year, year, year, year, year, year, year, year], "MPECType": ["Editorial", "Discovery", "OrbitUpdate", "DOU", "ListUpdate", "Retraction", "Other", "mpec_followup", "mpec_1st_followup"], "#MPECs": mpec_counts}), ignore_index = True)

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
            #no need to include 1stmpecfollowup since this is included in mpecfollowup

            editorials.clear()
            discoveries.clear()
            orbitupdates.clear()
            dous.clear()
            listupdates.clear()
            retractions.clear()
            others.clear()
            totalMPEC += sum(mpec_counts)
            FUcount += mpec_counts[7]
            F_FUcount += mpec_counts[8]

        '''if totalMPEC==0:
            blankStations.append(station)'''
        
        fig = px.bar(df, x="Year", y="#MPECs", color="MPECType", title= station.capitalize()+" | Number and type of MPECs by year")
        fig.write_html("C:\\Users\\taega\\OneDrive\\Documents\\mpec_files\\WEB_Stations\\Graphs\\{}.html".format(station))
        
        o += """    
          </div>
        </div>
        """
        #print("Total: ", totalMPEC)
        print("FUCount: ", FUcount)
        print("1stFUCount: ", F_FUcount)
        print(station)
        with open(page, 'w') as f:
            f.write(o)
    #print(blankStations)


'''start = time.perf_counter()
test_calcObs()   
finish = time.perf_counter()
print('Time: ', finish-start)'''

main()
mpecconn.close()
print('finished')