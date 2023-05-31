import sqlite3

mpecconn = sqlite3.connect("C:\\Users\\taega\\Documents\\mpec_files\\mpecwatch_v3.db")
cursor = mpecconn.cursor()

def tableNames():
    sql = '''SELECT name FROM sqlite_master WHERE type='table';'''
    cursor = mpecconn.execute(sql)
    results = cursor.fetchall()
    return(results[1::])

for station in tableNames():
    #Tuesday, April 14, 1998 7:30:25 PM
    sql = "SELECT MPEC FROM {} where MPECType != \"DOU\" and (Observer == \"\" and Measurer == \"\") and Time <=  892582225;".format(station[0])
    cursor = mpecconn.execute(sql)
    results = cursor.fetchall()
    # mal_MPECS = set()
    # for mpec in results:
    #     mal_MPECS.add(mpec[0])

    if (len(results) > 0):
        print(station[0], ": ", len(results))
        #print(mal_MPECS)
        