#other code used for testing MPECGraph

def test():
    cursor.execute("select Station from MPEC where DiscStation = Station")
    discStations = {}
    observations = cursor.fetchall()
    for observation in observations:
        discStations[observation] = discStations.get(observation,0)+1
    printDict(discStations)

d = dict()
def testTime():
    for station_name in tableNames():
        station = station_name[0][8::]
        print(station)
        d[station] = {}
        d[station]['mpec'] = {}
        d[station]['mpec_discovery'] = {}
        d[station]['mpec_followup'] = {}
        d[station]['mpec_1st_followup'] = {}
        d[station]['mpec_precovery'] = {}
        for y in np.arange(1993, currentYear+1, 1):
            timestamp_start = calendar.timegm(datetime.date(y,1,1).timetuple())
            timestamp_end = calendar.timegm(datetime.date(y+1,1,1).timetuple())-1
            
           ## numbers of MPECs
            cursor.execute("select station from MPEC where station like '%{}%' and time >= {} and time <= {};".format(station, timestamp_start, timestamp_end))
            d[station]['mpec'][y] = len(cursor.fetchall())
        
            ## numbers of discovery MPECs
            cursor.execute("select DiscStation from MPEC where DiscStation like '{}' and time >= {} and time <= {};".format(station, timestamp_start, timestamp_end))
            d[station]['mpec_discovery'][y] = len(cursor.fetchall())
        
            ## numbers of follow-up MPECs
            cursor.execute("select Station from MPEC where Station like '%{}%' and time >= {} and time <= {} and MPECType = 'Discovery' and DiscStation != '{}';".format(station, timestamp_start, timestamp_end, station))
            d[station]['mpec_followup'][y] = len(cursor.fetchall())
        
            ## numbers of first follow-up MPECs
            cursor.execute("select DiscStation, Station from MPEC where Station like '%{}%' and time >= {} and time <= {} and MPECType = 'Discovery' and DiscStation != '{}';".format(station, timestamp_start, timestamp_end, station))
            tmp = cursor.fetchall()
            c = 0
            for i in tmp:
                if i[0] + ', ' + station in i[1]:
                    c += 1
            
            d[station]['mpec_1st_followup'][y] = c
        
            ## numbers of precovery MPECs
            cursor.execute("select DiscStation, Station from MPEC where Station like '%{}%' and time >= {} and time <= {} and MPECType = 'Discovery' and DiscStation != '{}';".format(station, timestamp_start, timestamp_end, station))
            tmp = cursor.fetchall()
            c = 0
            for i in tmp:
                if bool(re.match('.*' + station + '.*' + i[0] + '.*', i[1])):
                    c += 1
                
            d[station]['mpec_precovery'][y] = c
    #printDict(d)

def testJ95():
    total = 0
    for y in np.arange(1993, currentYear+1, 1):
        y = int(y)
        timestamp_start = calendar.timegm(datetime.date(y,1,1).timetuple())
        timestamp_end = calendar.timegm(datetime.date(y+1,1,1).timetuple())-1
        cursor.execute("select station from MPEC where station like 'J95' and time >= {} and time <= {};".format(timestamp_start, timestamp_end))
        total += (len(cursor.fetchall()))
    print(total)
