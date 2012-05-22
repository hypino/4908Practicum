#!/usr/bin/env python
# -*- coding: latin-1 -*-

#
# BCIT COMP 4908 Practicum for
#
# Convergent Manufacturing Technologies Inc.
# 6190 Agronomy Road, Suite 403
# Vancouver, British Columbia, Canada
#
# Tyler Alison, Chris Sim, Mike Zobac
# 

"""
ClientHandler Prototypes

"""
import threading
import socket
import struct
import select

import ClientHandlerConstants as CHC
from database import DataHandler

"""
This class listens on a TCP port for client connections and accepts the connection.  It then adds the 
client to the list of connected clients
"""

class ClientListener(object):

    def __init__(self, dataHandler):
        self.__listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__listenSocket.bind((CHC.HOST, CHC.LISTENPORT))
        self.__listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__dataHandler = dataHandler
        self.__listLock = threading.Semaphore()
        self.__clientList = []
        self.__clientServer = ClientServer(self.__clientList, self.__listLock, self.__dataHandler)
        self.listen()
        
    def listen(self):
        self.__listenSocket.listen(1) #allows for a backlog of 5 sockets
        print "Listening for clients..."
        while(1):
            newSocket, newAdd = self.__listenSocket.accept()
            newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # attempt to gain access to the client list
            self.__clientList.append(newSocket)
            print "Client has connected."
    
    def setFirstTime(self, time):
        self.__firstRecordTime = time

class ClientServer(threading.Thread):

    def __init__(self, clientList, listLock, dataHandler):
        threading.Thread.__init__(self, name='Client/Server Thread')

        self.__clientList = clientList
        self.__listLock = listLock
        self.__localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__localSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__dataHandler = dataHandler
        
        while(1):	        
            try:  
                self.__localSocket.connect(CHC.LOCALDATA)
                print ("Local Connection established")
                self.__clientList.insert(0, self.__localSocket)
                break
            except:
                continue
        self.start()

    def run(self):

        print "Client/Server Running:"
        disconnected = []
        realTimeClients = []
        data = bytearray()
        
        while True:
            # wait for data from SensorDataCollector, or range requests from clients
            active = select.select(self.__clientList, [], [], CHC.SELECT_TIMEOUT)
            
            if len(active[0]) == 0:
                continue
           
            for sock in active[0]:
                # empty the buffer from previous passes
                del data[:]
                # if the local socket has data send it to the clients
                if sock is self.__localSocket:
                    # read data from self.localSocket
                    remaining = CHC.DATASIZE + 2
                    while remaining > 0:
                        recv = sock.recv(remaining)
                        data.extend(recv)
                        remaining -= len(recv)
                        
                    # attempt to gain access to the client list
                    # loop through the list and send the data to clients
                    for client in realTimeClients:
                        try:
                            client.send(data)
                        except:
                            #connection reset by peer
                            disconnected.append(client)
                    continue
                
                # otherwise, read requests from clients
                remaining = CHC.CLIENT_PACKET_SIZE
                try:
                    while remaining > 0:
                        recv = sock.recv(remaining)
                        if recv == '':
                            raise socket.error, "Connection reset by peer."
                        data.extend(recv)
                        remaining -= len(recv)
        
                    header, rangeStart, rangeEnd = struct.unpack("=cII", str(data))
                    if header == 'r':
                        print "Getting Ranges from %r to %r" % (rangeStart, rangeEnd)
                        rangeData = self.__dataHandler.getRangeData(rangeStart, rangeEnd)
                        totalLength = 0
                        for lst in rangeData:
                            totalLength = totalLength + len(lst)
                        print "totalLength: %r" % totalLength
                        length = struct.pack('=I', totalLength)
                        sock.send(length)
                        print "Sending length (%r rows)" % totalLength
                        
                        for lst in rangeData:
                            for row in lst:
                                string = struct.pack("=HIH8d", row[8], row[10], row[9], row[0], row[1],
                                                     row[2], row[3], row[4], row[5], row[6], row[7])
                                sock.send(str(string))
                                
                            
                    elif header == 't':
                        if sock not in realTimeClients:
                            realTimeClients.append(sock)
                            
                    elif header == 's':
                        if sock in realTimeClients:
                            realTimeClients.remove(sock)
                            sock.send('Z')
                    else:
                        raise TypeError, "Header is not defined"
                except socket.error:
                    disconnected.append(sock)
                
                # remove all disconnected clients
                for client in disconnected:
                    client.close()
                    if client in realTimeClients:
                        realTimeClients.remove(client)
                    self.__clientList.remove(client)
                    print "Client disconnected"
                    
                del disconnected[:]