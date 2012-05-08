import threading
import select
import socket
import os
import struct

from Sensor import Sensor
import database
from ClientHandlerConstants import LOCALDATA, DATASIZE

#Timeout for select to update it's sensor list if needed
SELECT_TIMEOUT = 0.1
"""Will collect data from all of the connected sensors

Thread that will constantly check all sensors for
more data to read. When data is read in, it will
be appended to the send buffer for clients to see
the real-time data. It will then be written to the
database.

Author: Tyler Allison
"""
class SensorDataCollector(threading.Thread):
    
    def __init__(self, sensorList):
	super(SensorDataCollector, self).__init__()
        self.__disconnected = []
        self.__sendBuffer = []
        self.__sensorList = sensorList
        self.__localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #Remove file if it exists from previous run
        try:
            os.remove(LOCALDATA)
	    print "deleting previous local socket"
        except OSError:
	    print "local socket didn't previously exist"
            pass
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
            if len(active) is 0:
	        continue
            for sensor in active[0]:
                self.__getSensorData(sensor)
            #write all data to database
            self.__appendToDatabase(self.__sendBuffer)
            #write all data to client handler
            for data in self.__sendBuffer:
                self.__localSend.send(data)
            #remove all sensors that disconnected
            for old in self.__disconnected:
                old.getSocket().close()
                self.__sensorList.remove(old)
            #clear lists
            del self.__sendBuffer[:]
            del self.__disconnected[:]
                
    def __getSensorData(self, sensor):
        #debugging
        assert isinstance(sensor, Sensor), "%s is not a Sensor" % sensor
        #get data from socket
	raw = bytearray(sensor.getSerial())
	sock = sensor.getSocket()
	remaining = DATASIZE
	while remaining > 0:
	    data = sock.recv(remaining)
	    raw.extend(data)
	    remaining -= len(data)
        #Did the sensor connection end? 2 because length of serial number. 
            #remove it later
            #self.__disconnected.append(sensor)
        #Append to sending buffer
        self.__sendBuffer.append(raw)
        
    def __appendToDatabase(self, data):
        for line in data:
            row = struct.unpack('!hih8d', line)
            database.DataHandler.appendRow(row)
            