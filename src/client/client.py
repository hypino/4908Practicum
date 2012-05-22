import threading
import struct
import socket
import signal
from os import kill
from time import sleep

import clientConstants as CC

class Client():
    
    def __init__(self, host=CC.LOCALHOST):
        self.__collector = None
        self.__host = host
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # connect to server        
        print "Connecting to server %s" % self.__host
        while(1):        
            try:        
                self.__socket.connect((host, CC.HOSTPORT))
                print "Connected"
                break
            except:
                continue
        self.run()
    
    def getSocket(self):
        return self.__socket
        
        
    def run(self):
        while(1):
            print "Enter r for range data or t for real-time data.  s to stop:"
            
            selection = raw_input()
            
            if selection == 'r':
                if self.__collector != None and self.__collector.isAlive():
                    data = struct.pack("=cII", 's' , 0, 0)
                    self.__socket.send(data)
                
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
                print "Waiting for length..."
                length = self.__socket.recv(4)
                numRows = struct.unpack('=I', length)
                print "Received length, expecting %r rows" % numRows[0]
                self.__collector = UICollector('h', int(numRows[0]), self.__socket)
                self.__collector.join()
                continue
                
            elif selection == 't':
                try:
                    self.__realTimeFile = open("realTimeFile", 'w')
                except:
                    pass
                data = struct.pack("=cII", 't' , 0, 0)
                self.__socket.send(data)
                self.__collector = UICollector('r', -1, self.__socket)
                continue
                
            elif selection == 's':
                if self.__collector != None and self.__collector.isAlive():
                    data = struct.pack("=cII", 's' , 0, 0)
                    self.__socket.send(data)
                    self.__collector.join()
                continue
                
            else:
                print "Huh?"
            
class UICollector(threading.Thread):
    
    def __init__(self, type, length, socket):
    
        threading.Thread.__init__(self, name='UI ineraction thread')
        if type == 'r':
            self.__realTimeFile = open("realTimeFile", 'w')
        else:
            self.__historyFile = open("historyFile", 'w')
        self.__type = type
        self.__length = length
        self.__socket = socket
        self.start()
        
    def run(self):
        self.getData(self.__length)

    def getData(self, length):
        count = 0
        while(length == -1 or length > 0):
            remaining = CC.DATASIZE   
            data = bytearray("")
            #Read realtime data from the socket
            if self.__socket.recv(1, socket.MSG_PEEK) == 'Z':
               self.__socket.recv(1)
               break
            
            while remaining > 0:
                try:
                    recv = self.__socket.recv(remaining)
                    data.extend(recv)
                    remaining -= len(recv)
                except socket.error:
                    print "failed to receive on this iteration"
                    exit(1)
            self.displayData(data)
            
            if length != -1:
                length = length - 1
        
        if self.__type == 'r':
            self.__realTimeFile.close()
        else:
            self.__historyFile.close()
            
    def displayData(self, data):
        # unpack the data: Serial No, Seconds, MilliSeconds, 8 * Data
        line = struct.unpack('=HIH8d', str(data))
        string = [str(line[i]) for i in xrange(len(line))]
        
        if self.__type == 'r':
            self.__realTimeFile.write(' '.join(string))
            self.__realTimeFile.write('\n')
        
        elif self.__type == 'h':
            self.__historyFile.write(' '.join(string))
            self.__historyFile.write('\n')
            
        else:
            return
