import threading
#from database import DataHandler
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
        #db = DataHandler()
        self.__ui = UICollector()
        self.__ui.start()
        getData()
        
    
    
    def getHistoryData(self):
    
        remaining = CC.DATASIZE    
	    
        while remaining > 0:
	        recv = self.__socket.recv(remaining)
	        data.extend(recv)
	        remaining -= len(recv)
	        
    """
    Read real-time sensor data from client and save it to the DB.  Display it if 
    real-time mode is enabled
    """
    def getRealTimeData(self):
        
        #  FIX THIS TO CATCH SIGINT!!!!!!
        while (1):
            remaining = CC.DATASIZE    
	        
            # Read realtime data from the socket
            while remaining > 0:
	            recv = self.__socket.recv(remaining)
	            data.extend(recv)
	            remaining -= len(recv)
            
            # display data
            if self.__realTime:
                print data
        

   
 #class UICollector(threading.Thread):
