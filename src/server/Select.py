import threading
import select
import socket

import Sensor

#Expected size of the packet data from a sensor
BUFFER_SIZE = 70
#Connected sensors
numConnected = 0
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
        self.__sensorList = sensorList
        self.run()
        
    def run(self):
        while True:
            # wait for data from sensors, wlist and xlist can be empty
            active = select.select(self.__sensorList, [], [])
            #initialize send buffer
            sendBuffer = []            
            for sensor in active[0]:
                getSensorData(sensor, sendBuffer)
            #write all data to database
            #write all data to sending buffer
                
    def getSensorData(self, sensor, sendBuffer):
        #debugging
        assert isinstance(sensor, Sensor.Sensor), "%s is not a socket descriptor" % sensor
        
        #get data from socket
        raw = sensor.fileno().recv(BUFFER_SIZE)
        assert len(raw) == BUFFER_SIZE, "Data received not %d bytes" % BUFFER_SIZE 
        
        #Append to sending buffer
        sendBuffer.append(raw)
        