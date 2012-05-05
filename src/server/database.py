import tables
import numpy
import datetime

class Record(tables.IsDescription):
    # columns
    serialNum = Int32Col()
    timeSec = Int32Col()
    timeMilli = Int32Col()
    col1 = Float64Col()
    col2 = Float64Col()
    col3 = Float64Col()
    col4 = Float64Col()
    col5 = Float64Col()
    col6 = Float64Col()
    col7 = Float64Col()
    col8 = Float64Col()

class DataHandler():
    
    def __init__(self):
        dataFile = openFile('SensorDatabase', mode = "w", title = "Sensor data file")
        dataFile.createGroup("/", 'sensorData', 'Group of data from sensors')
        dataFile.createTable(group, 'data', Record, "Data since %s" % datetime.now())
        dataFile.close()
    
    def appendRow((serialNum, timeSec, timeMilli, col1, col2, col3, col4, col5, col6, col7, col8)):
        #open PyTables table
        dataFile = openFile('SensorDatabase', mode = "a", title = "Sensor data file")
        #get the data table
        table = dataFile.root.sensorData.data
        row = table.row
        
        # instead of 10 in xrange(10), put number of sensors
        for i in xrange(10):
            row['serialNum'] = serialNum
            row['timeSec'] = timeSec
            row['timeMilli'] = timeMilli
            row['col1'] = col1
            row['col2'] = col2
            row['col3'] = col3
            row['col4'] = col4
            row['col5'] = col5
            row['col6'] = col6
            row['col7'] = col7
            row['col8'] = col8
            # adding this row to the table
            row.append()
            
        # this saves the table to the file    
        table.flush()
        dataFile.close()