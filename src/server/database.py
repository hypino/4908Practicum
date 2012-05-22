import struct
from datetime import datetime
from threading import Lock

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
displayedData = 1000

class DataHandler(object):

    def __init__(self):
        self.__lock = Lock()
        self.__dataFile = openFile('SensorDatabase', mode = 'a', title = 'Sensor data file')
        
    def createSensorTable(self, name):
        self.__lock.acquire()
        group = self.__dataFile.root
        tables = group._v_children
        newGroup = True
        for node in self.__dataFile.listNodes('/'):
            if len(node._v_children) < 10:
                newGroup = False
                useGroup = node
                break
        if newGroup:
            useGroup = self.__dataFile.createGroup('/', str(len(tables)+1), '')
        newTable = True
        for node in self.__dataFile.listNodes('/'):
            if name in node:
                newTable = False
        if newTable:
            self.__dataFile.createTable(useGroup, name, Record, 'Data since %s' % datetime.now())
        self.__lock.release()

    def appendRows(self, data):
        #acquire database
        self.__lock.acquire()
        #get the data table
        nodes = self.__dataFile.listNodes('/')

        numRows = len(data)
        for i in xrange(numRows):
            line = struct.unpack('=HIH8d', str(data[i]))
            for group in nodes:
                tables = group._v_children
                for sensor in tables:
                    if sensor == str(line[0]):
                        table = tables[sensor]
                        break
            row = table.row
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
            table.flush()

        #release database
        self.__lock.release()

    def getRangeData(self, startTime, finishTime, serial=None):
        #acquire database
        self.__lock.acquire()
        nodes = self.__dataFile.listNodes('/')
        
        dataList = []
        rangeData = finishTime - startTime
        
        if rangeData > displayedData:
            stepVal = (rangeData * 100)/ displayedData
        else:
            stepVal = 1
        
        cond = '(timeSec >= startTime) & (timeSec <= finishTime)'
        condvars = {'startTime' : startTime, 'finishTime' : finishTime}
        
        for group in nodes:
            tables = group._v_children
            for table in tables:
                result = [row.fetch_all_fields() for row in tables[table].where(cond, condvars, step = stepVal)]
                dataList.append(result)       
        self.__lock.release()   
        
        return dataList

    
class sortData(object):
    
    def __init__(self):
        self.result = []
    
    def merge(self, left, right):
        i ,j = 0, 0
        while i < len(left) and j < len(right):
            if left[i][8] <= right[j][8]:
                self.result.append(left[i])
                i += 1
            else:
                self.result.append(right[j])
                j += 1
        self.result += left[i:]
        self.result += right[j:]
        return self.result        
                
    def mergesort(self, list):
        if len(list) < 2:
            return list
        middle = len(list) / 2
        left = self.mergesort(list[:middle])
        right = self.mergesort(list[middle:])
        return self.merge(left, right)    
    
    def quicksort(self, list):
        return [] if list==[]  else self.quicksort([x for x in list[1:] if x[8] < list[0][8]]) + [list[0]] + self.quicksort([x for x in list[1:] if x[8] >= list[0][8]])
    