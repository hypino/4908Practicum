from os import path

import struct
from datetime import datetime
from threading import Semaphore

from tables import *
import numpy

"""Record is the layout of a row of data
in the PyTables file. Each row will be
constructed exactly like this.

"""



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

"""This object will be the central
access point to the database for all
threads of the program.

It should be noted that each function
of this class first acquires the semaphore,
and lastly releases the semaphore. All
additional methods should do the same.
This object can be treated like a Monitor.

"""

READCOUNT = 1000

class DataHandler(object):
    
    def __init__(self):
        self.__lock = Semaphore()
	if not path.exists('SensorDatabase'):
            self.__dataFile = openFile('SensorDatabase', mode = 'w', title = 'Sensor data file')
	    group = self.__dataFile.createGroup('/', 'sensorData', 'Group of data from sensors')
	    self.__dataFile.createTable(group, 'data', Record, 'Data since %s' % datetime.now())	    
	else:
	    self.__dataFile = openFile('SensorDatabase', mode = 'a', title = 'Sensor data file')
        self.__firstRead = True
        
        #dataFile.close()
    
    def appendRows(self, data):
        #acquire database
        self.__lock.acquire()
        #open PyTables table
        #dataFile = openFile('SensorDatabase', mode = "a", title = "Sensor data file")
        #get the data table
        table = self.__dataFile.root.sensorData.data
        row = table.row
        
        numRows = len(data)
        
        # instead of 10 in xrange(20), put number of sensors
        for i in xrange(numRows):
            line = struct.unpack('=HIH8d', str(data[i]))
            row['serialNum'] = line[0]
            row['timeSec'] = line[1]
            row['timeMilli'] = line[2]
            row['col1'] = line[3]
            row['col2'] = line[4]
            row['col3'] = line[5]
            row['col4'] = line[6]
            row['col5'] = line[7]
            row['col6'] = line[8]
            row['col7'] = line[9]
            row['col8'] = line[10]
            # adding this row to the table
            row.append()
            
        # this saves the table to the file    
        table.flush()
        #dataFile.close()
        #release database
        self.__lock.release()
        
        
    def getRealTimeData(self):
        # acquire database
        self.__lock.acquire()
        # open PyTables table
        #dataFile = openFile('SensorDatabase', mode = "r", title = "Sensor data file")
        # get the data table
        table = self.__dataFile.root.sensorData.data
        row = table.row

        # in theory, this should return the last row in that table
        # what it does is it returns the "curent" row
        result = row.nrow()
        
        #dataFile.close()
        # release database
        self.__lock.release()
        return result
        
    def getRangeData(self, startTime, finishTime):
        #acquire database
        self.__lock.acquire()
        #open PyTables table
        #dataFile = openFile('SensorDatabase', mode = "r", title = "Sensor data file")
        #get the data table
        table = self.__dataFile.root.sensorData.data
        row = table.row
        
        result = [i['timeSec'] for i in table.where('''(finishTime >= timeSec) & (timeSec >= startTime)''')]
        
        #dataFile.close()
        #release database
        self.__lock.release()
        return result
    
    def sendDB(self):
	# acquir database
	self.__lock.acquire()
        # close the db
        self.__dataFile.close()
        # open the file in binary mode
        self.__dataFile = open('SensorDatabase', mode = 'rb')
        if not self.__firstRead:
            # read from where we left off
            self.__dataFile.seek(self.__filePosition)
        
        # read a bunch of data    
        count = 0
	data = bytearray("")
        while count < READCOUNT:
	    line = self.__dataFile.readline()
	    if line == "":
		break
	    data.extend(line)
	    count += 1
        
        # save where we are in the file
        self.__filePosition = self.__dataFile.tell()
        self.__dataFile.close()
        
        # re open the db in append mode
        self.__dataFile = openFile('SensorDatabase', mode = 'a', title = 'Sensor data file')
        self.__lock.release()
        if self.__firstRead:
            self.__firstRead = False
	    	    
	return(data)