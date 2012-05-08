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
import pipes


import ClientHandlerConstants as CHC


"""
This class listens on a TCP port for client connections and accepts the connection.  It then creates 
an instance of ClientAdder, which updates the new client's data, adds the client to the list of connected clients
"""

class ClientListener():
    
    def __init__(self):
        self.__listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__listenSocket.bind((CHC.HOST, CHC.LISTENPORT))
	self.__listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__listLock = threading.Semaphore()
        self._clientList = []
        self.__clientServer = ClientServer(self._clientList, self.__listLock)
        self.listen()
    
    def listen(self):
        while(1):
            self.__listenSocket.listen(5) #allows for a backlog of 5 sockets
            newSock, newAdd = self.__listenSocket.accept()
            newSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            adder = ClientAdder(newSock, self._clientList, self.__listLock)




class ClientAddr(threading.Thread):
    
    def __init__(self, clientSocket, clientList, clientListLock):
        threading.Thread.__init__(self, name='client_addition_thread')
        
        self.__clientSocket = clientSocket
        self.__clientList = clientList
        self.__listLock = clientListLock 
        self.run()
            
    def run(self):
        
	    # read history from pytable and send to new client	

	    # while still reading the db 
		    # data = read hunk from database
            # self.clientSocket.send(data)
		    
        self.__listLock.acquire()  # attempt to gain access to the client list
        self.__clientList.append(self.__clientSocket)
        self.__listLock.release()




class ClientServer(threading.Thread):
    
    def __init__(self, clientList, listLock):
        threading.Thread.__init__(self, name='client_addition_thread')
            
        self.__clientList = clientList
        self.__listLock = listLock
        self.__localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__localSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while(1):	        
            try:  
		sleep(1)
                self.__localSocket.connect(CHC.LOCALDATA)
                print ("local Connection")
                break
            except:
                continue
	    self.run()
            
    def run(self):
        
        data = []
        
        while(1):
            
            # read data from self.localSocket
            while len(data) < CHC.DATASIZE:
                data.append(self.__localSocket.recv(CHC.DATASIZE))
            
            stringData = ''.join(data)
            # attempt to gain access to the client list
            self.__listLock.acquire()
            # loop through the list and send the data to clients
            self.__listLock.release() # release the list
            #empty local data list
            del data[:]
            
            
            
