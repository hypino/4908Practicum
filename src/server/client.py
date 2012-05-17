import threading
from database import DataHandler
import struct
import socket
import signal
from os import kill

import clientConstants as CC

class Client():
    
    def __init__(self, host=CC.LOCALHOST):
        
        self.__realTime = True        
        self.__host = host        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # connect to server        
        while(1):        
            try:        
                self.__socket.connect((host, CC.HOSTPORT))
                print "Connected"
                break
            except:
                continue
        
        #self.__ui = UICollector()
        #self.__ui.start()
        
        
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
            # write packet to db 
            self.__db.appendRows([str(data)])
            if self.__realTime: 
                self.displayData(data)
        
    def displayData(self, data):
        
        # This will be replaced by a better display method this week.
                
        # display data
        if self.__realTime:
            print data

    def getHistory(self):
        
        self.__socket.settimeout(1)        
        dataFile = open("SensorDatabase", 'wb')        
        while (1):
            try:	        
                recv = self.__socket.recv(4096)
                dataFile.write(recv)
            except socket.timeout:
                break
                

        dataFile.close()
        self.__socket.settimeout(None)
        self.__db = DataHandler()
        self.getRealTimeData()
        

    def shutdown(self):
	#self.__ui.shutdown()
	pid = getpid()
	os.kill(pid, signal.SIGTERM)

 #class UICollector(threading.Thread):
