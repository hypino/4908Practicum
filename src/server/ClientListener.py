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
This class listens on a TCP port for client connections and accepts the connection.  It then creates 
an instance of ClientAdder, which updates the new client's data, adds the client to the list of connected clients
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
        self.__firstRecordTime = 0
        self.listen()
        
    def listen(self):
        self.__listenSocket.listen(5) #allows for a backlog of 5 sockets
        print "Listening for clients..."
        while(1):
            newSocket, newAdd = self.__listenSocket.accept()
            newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__listLock.acquire()  # attempt to gain access to the client list
            self.__clientList.append(newSocket)
            self.__listLock.release()
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
                self.__listLock.acquire()
                self.__clientList.insert(0, self.__localSocket)
                self.__listLock.release()
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
            self.__listLock.acquire()
            # wait for data from SensorDataCollector, or range requests from clients
            active = select.select(self.__clientList, [], [], CHC.SELECT_TIMEOUT)
            self.__listLock.release()
            
            if len(active[0]) == 0:
                continue
           
            for socket in active[0]:
                # empty the buffer from previous passes
                del data[:]
                # if the local socket has data send it to the clients
                if socket is self.__localSocket:
                    # read data from self.localSocket
                    remaining = CHC.DATASIZE + 2
                    while remaining > 0:
                        recv = socket.recv(remaining)
                        data.extend(recv)
                        remaining -= len(recv)
                        
                    # attempt to gain access to the client list
                    self.__listLock.acquire()
                    # loop through the list and send the data to clients
                    for client in realTimeClients:
                        try:
                            client.send(data)
                        except:
                            #connection reset by peer
                            disconnected.append(client)
                            continue
                        
                    self.__listLock.release() # release the list
                    continue
                
                # otherwise, read range requests from clients
                remaining = CHC.CLIENT_PACKET_SIZE
                try:
                    while remaining > 0:
                        recv = socket.recv(remaining)
                        if recv == '':
                            raise Exception, "Connection reset by peer."
                        data.extend(recv)
                        remaining -= len(recv)
        
                    header, rangeStart, rangeEnd = struct.unpack("=cII", str(data))
                    
                    if header == 'r':
                        realTimeClients.remove(socket)
                        rangeData = self.__dataHandler.getRangeData(rangeStart, rangeEnd)
                        socket.send(rangeData)
                    elif header == 't':
                        realTimeClients.append(socket)
                    elif header == 's':
                        realTimeClients.remove(socket)
                    else:
                        raise Exception, "Header is not defined"
                except:
                    disconnected.append(socket)
                    continue
                
                # remove all disconnected clients
                for close in disconnected:
                    close.close()
                    self.__listLock.acquire()
                    self.__clientList.remove(close)
                    self.__listLock.release()
                    print "Client disconnected"
                del disconnected[:]