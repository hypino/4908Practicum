import threading
from database import DataHandler
import struct
import socket


import clientConstants as CC

class Client():
    
    def __init__(self, host=CC.LOCALHOST):
        
        self.__realTime = True        
        self.__host = host        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.connect((host, CC.HOSTPORT))
        #self.__ui = UICollector()
        #self.__ui.start()
        self.__historyCollector = HistoryCollector(self)
        
        
    """
    Read real-time sensor data from client and save it to the DB.  Display it if 
    real-time mode is enabled
    """
    def getRealTimeData(self):
        
        while (1):
            remaining = CC.DATASIZE    
	        
            data = bytearray("")
            # Read realtime data from the socket
            while remaining > 0:
	            recv = self.__socket.recv(remaining)
	            data.extend(recv)
	            remaining -= len(recv)
            
            if CC.REALTIMEMODE: 
                self.displayData(data)
        
    def displayData(self, data):
        
        # This will be replaced by a better display method this week.
                
        # display data
        if self.__realTime:
            print data

class HistoryCollector(threading.Thread):

    def __init__(self, client):
        super(HistoryCollector, self).__init__()
        self.__client = client
        self.start()
   
    def run(self):
    
        dataFile = open("SensorDatabase", 'wb')        
        remaining = 0        
        while remaining > 0:
	        recv = self.__socket.recv(remaining)
	        dataFile.write(recv)
	        remaining -= len(recv)

        dataFile.close()
        db = DataHandler()
        self.__client.getRealTimeData()
        CC.DATABASEREADY = True

 #class UICollector(threading.Thread):
