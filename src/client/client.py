import threading
import struct
import socket
import signal
from os import kill

import clientConstants as CC

class Client():
    
    def __init__(self, host=CC.LOCALHOST):
        
        self.__file = open("datafile", 'w')
        self.__realTime = True        
        self.__host = host        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # connect to server        
        print "Connecting to server"
        while(1):        
            try:        
                self.__socket.connect((host, CC.HOSTPORT))
                print "Connected"
                break
            except:
                continue
        
        self.__ui = UICollector(self)
        self.getData()
        
    def getSocket(self):
        return self.__socket
        
    def getRealtime(self):
        return self.__realTime
        
    def setRealtime(self, setting):
        self.__realTime = setting
        
    """
    Read real-time sensor data from client and display it if 
    real-time mode is enabled
    """
    def getData(self):
        
        while (1):
            
			remaining = CC.DATASIZE    
			data = bytearray("")
            # Read realtime data from the socket
            
			while remaining > 0:
				recv = self.__socket.recv(remaining)
				data.extend(recv)
				remaining -= len(recv)
					
			self.displayData(data)
        
    def displayData(self, data):
        # unpack the data: Serial No, Seconds, MilliSeconds, 8 * Data
        line = struct.unpack('=HIH8d', str(data))
        string = [str(line[i]) for i in xrange(len(line))]
        self.__file.write(' '.join(string))
        self.__file.write('\n')

    
    
class UICollector(threading.Thread):
    
    def __init__(self, client):
    
        threading.Thread.__init__(self, name='UI ineraction thread')
        
        self.__client = client
        self.start()
        
    def run(self):
        while(1):
            print "Enter r for range data or t for real-time data:"
            
            try:
				selection = raw_input()
            except KeyboardInterrupt:
				continue
            
            if selection == 'r':
                self.__client.setRealtime(False)
                print "Enter Start of Range:"
                try:
					rangeStart = raw_input()
					start = atoi(rangeStart)    
                except KeyboardInterrupt:
					continue
                
                print "Enter End of Range:"
                try:
					rangeEnd = raw_input()
					end = atoi(rangeEnd)    
                except KeyboardInterrupt:
					continue
					
                socket = self.__client.getSocket()
                data = struct.pack("II", start, end)
                socket.send(data)
                continue
                
            elif selection == 't':
                self.__client.setRealtime(True)
                continue
                
            else:
                print "Huh?"
        
