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
        self._clientList = []
        self.__clientServer = ClientServer(self._clientList, self.__listLock, self.__dataHandler)
        self.listen()
    """   
    def __del__(self):
        
        self.__listLock.acquire()
        for client in self._clientList:
            client.shutdown(socket.SHUT_RDWR)
        self.__listenSocket.shutdown(socket.SHUT_RDWR)
        exit(0)
    """
    def listen(self):
        self.__listenSocket.listen(5) #allows for a backlog of 5 sockets
        print "Listening for clients..."
        while(1):
            newSocket, newAdd = self.__listenSocket.accept()
            newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__listLock.acquire()  # attempt to gain access to the client list
            self._clientList.append(newSocket)
            self.__listLock.release()
            print "Client has connected."

class ClientServer(threading.Thread):

    def __init__(self, clientList, listLock, dataHandler):
        threading.Thread.__init__(self, name='client_addition_thread')

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
        
        
        while True:
            
            data = bytearray()
            self.__listLock.acquire()

            # wait for data from SensorDataCollector, or range requests from clients
            active = select.select(self.__clientList, [], [], CHC.SELECT_TIMEOUT)
            self.__listLock.release()
            
            if len(active[0]) == 0:
                continue
            
            for socket in active[0]:
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
                    for client in self.__clientList[1:]:
                        try:
                            client.send(data)
                        except:
                            #connection reset by peer
                            disconnected.append(client)
                    self.__listLock.release() # release the list
                    continue
                
                # otherwise, read range requests from clients
                timeRange = []
                remaining = CHC.HISTORYSIZE
                try:
                    while remaining > 0:
                        recv = socket.recv(remaining)
                        timeRange.append(recv)
                        remaining -= len(recv)
                        
                    rangeStart, rangeEnd = struct.unpack("II", timeRange)
                    # get range data from db
                    rangeData = self.__dataHandler.getRangeData(rangeStart, rangeEnd)
                    
                    #send range data to client
                    socket.send(rangeData)
                except:
                    #connection reset by peer
                    disconnected.append(client)
                
                #remove all disconnected clients
                for close in disconnected:
                    close.close()
                    self.__clientList.remove(close)
                    print "Client disconnected"
                del disconnected[:]
                del data[:]
                del timeRange[:]