import threading
import select
import socket

import Sensor

LOCALHOST = '127.0.0.1'
LOCALPORT = 51011
#Expected size of the packet data from a sensor
BUFFER_SIZE = 70
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
        self.__disconnected = []
        self.__sensorList = sensorList
        self.__sendBuffer = []
        self.__localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__localSocket.bind((LOCALHOST, LOCALPORT))
        self.__localSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.run()
        
    def run(self):
        while True:
            # wait for data from sensors, wlist and xlist can be empty
            active = select.select(self.__sensorList, [], [])
            for sensor in active[0]:
                getSensorData(sensor)
            #write all data to database
            #write all data to client handler
            for data in self.__sendBuffer:
                self.__localSocket.send(data)
            #remove all sensors that disconnected
            for old in self.__disconnected:
                self.__sensorList.remove(old)
            #clear list
            del self.__sendBuffer[:]
            del self.__disconnected[:]
                
    def getSensorData(self, sensor:
        #debugging
        assert isinstance(sensor, Sensor.Sensor), "%s is not a socket descriptor" % sensor
        
        #get data from socket
        raw = sensor.fileno().recv(BUFFER_SIZE)
        
        #Did the sensor connection end?
        if(len(raw) == 0):
            #remove it later
            self.__disconnected.append(sensor)
        
        #Append to sending buffer
        self.__sendBuffer.append(raw)
        