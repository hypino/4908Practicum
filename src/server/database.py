from tables import *
import numpy
from datetime import datetime
from threading import Semaphore

class Record(IsDescription):
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
        self.__lock = Semaphore()
        dataFile = openFile('SensorDatabase', mode = "w", title = "Sensor data file")
        group = dataFile.createGroup("/", 'sensorData', 'Group of data from sensors')
        dataFile.createTable(group, 'data', Record, "Data since %s" % datetime.now())
        dataFile.close()
    
    @staticmethod
    def appendRow(self, data):
        assert len(data) == 11, "Data is not formatted correctly for database"
        #acquire database
        self.__lock.acquire()
        #open PyTables table
        dataFile = openFile('SensorDatabase', mode = "a", title = "Sensor data file")
        #get the data table
        table = dataFile.root.sensorData.data
        row = table.row
        
        # instead of 10 in xrange(20), put number of sensors
        for i in xrange(20):
            row['serialNum'] = data[0]
            row['timeSec'] = data[1]
            row['timeMilli'] = data[2]
            row['col1'] = data[3]
            row['col2'] = data[4]
            row['col3'] = data[5]
            row['col4'] = data[6]
            row['col5'] = data[7]
            row['col6'] = data[8]
            row['col7'] = data[9]
            row['col8'] = data[10]
            # adding this row to the table
            row.append()
            
        # this saves the table to the file    
        table.flush()
        dataFile.close()
        #release database
        self.__lock.release()
        
        
    @staticmethod
    def getRealTimeData(self):
        # acquire database
        self.__lock.acquire()
        # open PyTables table
        dataFile = openFile('SensorDatabase', mode = "r", title = "Sensor data file")
        # get the data table
        table = dataFile.root.sensorData.data
        row = table.row

        # in theory, this should return the last row in that table
        # what it does is it returns the "curent" row
        print row.nrow()

        dataFile.close()
        # release database
        self.__lock.release()
        
    
    @staticmethod
    def getRangeData(self, startTime, finishTime):
        #acquire database
        self.__lock.acquire()
        #open PyTables table
        dataFile = openFile('SensorDatabase', mode = "a", title = "Sensor data file")
        #get the data table
        table = dataFile.root.sensorData.data
        row = table.row
        
        result = [i['timeSec'] for i in table.where("""(finishTime >= timeSec) & (timeSec >= startTime)""")]
        print result
       
        dataFile.close()
        #release database
        self.__lock.release()    
