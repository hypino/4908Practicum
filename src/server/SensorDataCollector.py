import threading
import select
import socket
import os
import struct

from Sensor import Sensor
from database import DataHandler
from ClientHandlerConstants import LOCALDATA, DATASIZE, SELECT_TIMEOUT

#Timeout for select to update it's sensor list if needed
"""Will collect data from all of the connected sensors

Thread that will constantly check all sensors for
more data to read. When data is read in, it will
be appended to the send buffer for clients to see
the real-time data. It will then be written to the
database.

Author: Tyler Allison
"""
class SensorDataCollector(threading.Thread):
    
    def __init__(self, sensorList, dataHandler):
	super(SensorDataCollector, self).__init__()
	self.__database = dataHandler
        self.__disconnected = []
        self.__sendBuffer = []
        self.__sensorList = sensorList
        self.__localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #Remove file if it exists from previous run
        try:
            os.remove(LOCALDATA)
	    print "Deleting previous local socket."
        except OSError:
	    print "Local socket didn't previously exist, creating."
        #Create the socket at the file location
        self.__localSocket.bind(LOCALDATA)
        self.__localSocket.listen(1)
        self.__localSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #Need to wait until the server connects before we can start
        self.start()
        
    def run(self):
	#self.__localSend, self.__localAddr = self.__localSocket.accept()
        while True:
            # wait for data from sensors, wlist and xlist can be empty
            active = select.select(self.__sensorList, [], [], SELECT_TIMEOUT)
            if len(active[0]) == 0:
	        continue
            for sensor in active[0]:
                self.__getSensorData(sensor)
            #write all data to database
	    if len(self.__sendBuffer) != 0:
		self.__appendToDatabase(self.__sendBuffer)
            #write all data to client handler
            #for data in self.__sendBuffer:
            #    self.__localSend.send(data)
            #remove all sensors that disconnected
            for old in self.__disconnected:
                old.getSocket().close()
                self.__sensorList.remove(old)
		print "Sensor %r disconnected" % old.getSerial() 
            #clear lists
            del self.__sendBuffer[:]
            del self.__disconnected[:]
                
    def __getSensorData(self, sensor):
        assert isinstance(sensor, Sensor), "%s is not a Sensor" % sensor
	raw = bytearray(struct.pack('H', sensor.getSerial()))
	sock = sensor.getSocket()
	remaining = DATASIZE
	try:
	    check = sock.recv(1, socket.MSG_PEEK)
	    #if the sensor has no data currently, return
	    if check == '\x00':
		sock.recv(1)
		return
	    #read a whole packet (DATASIZE bytes)
	    while remaining > 0:
		data = sock.recv(remaining)
		raw.extend(data)
		remaining -= len(data)
	    #Append to sending buffer
	    self.__sendBuffer.append(raw)
	except:
	    #connect reset by peer
	    self.__disconnected.append(sensor)
	    return	
        
    def __appendToDatabase(self, data):
	self.__database.appendRows(data)
            