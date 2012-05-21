import threading
import struct
import socket
import signal
from os import kill
from time import sleep

import clientConstants as CC

class Client():
    
    def __init__(self, host=CC.LOCALHOST):
        
        self.__realTimeFile = open("realTimeFile", 'w')
        self.__historyFile = open("historyFile", 'w')
        self.__realTime = True
        self.__history = False

        self.event = threading.Event()        
        self.__host = host        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(.1)
        self.__firstRecordTime = 0
        self.event = threading.Event()
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
        
    def setHistory(self, setting):
        self.__history = setting
        
    def setRealtime(self, setting):
        self.__realTime = setting
        
    def setHistory(self, setting):
        self.__history = setting
        
    def closeHistoryFile(self):
        self.__historyFile.close()
        
    def closeRealtimeFile(self):
        self.__realTimeFile.close()
        
    def closeDataFiles(self):
        self.closeHistoryFile()
        self.closeRealtimeFile()
        
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

                try:
                    recv = self.__socket.recv(remaining)
                    data.extend(recv)
                    remaining -= len(recv)
                except socket.timeout:
                    self.event.set()
                    self.event.clear()
                    continue
                

            self.displayData(data)
        
    def displayData(self, data):
        # unpack the data: Serial No, Seconds, MilliSeconds, 8 * Data
        line = struct.unpack('=HIH8d', str(data))
        string = [str(line[i]) for i in xrange(len(line))]
        
        if self.__realTime:
            self.__realTimeFile.write(' '.join(string))
            self.__realTimeFile.write('\n')
        
        elif self.__history:

            self.__historyFile.write(' '.join(string))
            self.__historyFile.write('\n')
            
        else:
            return
            
            
class UICollector(threading.Thread):
    
    def __init__(self, client):
    
        threading.Thread.__init__(self, name='UI ineraction thread')
        event = threading.Event()
        self.__client = client
        self.__socket = self.__client.getSocket()
        self.start()
        
    def run(self):
        while(1):
            print "Enter r for range data or t for real-time data.  s to stop:"
            
            try:
				selection = raw_input()
            except KeyboardInterrupt:
				continue
            
            if selection == 'r':
                self.__client.event.clear()
                data = struct.pack("=cII", 's' , 0, 0)
                self.__socket.send(data)
                

                self.__client.event.wait()
                self.__client.setRealtime(False)
                self.__client.setHistory(True)

                try:
                    self.__historyFile = open("historyFile", 'w')
                except:
                    pass
                

                self.__client.event.wait()
                
                self.__client.setHistory(True)

                
                print "Enter Start of Range:"
                try:
					rangeStart = raw_input()
					start = int(rangeStart)    
                except KeyboardInterrupt:
					continue
                
                print "Enter End of Range:"
                try:
					rangeEnd = raw_input()
					end = int(rangeEnd)    
                except KeyboardInterrupt:
					continue
					
                data = struct.pack("=cII", 'r', start, end)
                self.__socket.send(data) 
                
                self.__client.event.wait()
                self.__client.closeHistoryFile()
                self.__client.setHistory(False)
                continue
                
            elif selection == 't':

                self.__client.setRealtime(True)

                try:
                    self.__realTimeFile = open("realTimeFile", 'w')
                except:
                    pass
                self.__client.setRealtime(True)
                data = struct.pack("=cII", 't' , 0, 0)
                self.__socket.send(data)
                continue
                
            elif selection == 's':
                self.__client.setRealtime(False)
                data = struct.pack("=cII", 's' , 0, 0)
                self.__socket.send(data)
                self.__client.closeDataFiles
                
                continue
                
            else:
                print "Huh?"
        
