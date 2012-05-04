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
ClientServer

"""

import socket
import threading

import ClientHandlerConstants as CHC

class ClientServer(threading.Thread):
    
    def __init__(self, clientList, listLock):
            threading.Thread.__init__(self, name='client_addition_thread')
            
            self.__clientList = clientList
            self.__listLock = listLock
            self.__localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.__localSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	    self.__localSocket.connect(LOCALDATA)
            
    def run(self):
        
        while(1):
            
            # read data from self.localSocket
            data = []
            while len(data) < CHC.DATASIZE:
                data.append(self.__localSocket.recv(CHC.DATASIZE))
            
            stringData = ''.join(data)    
            self.listLock.acquire() # attempt to gain access to the client list
            # loop through the list and send the data to clients
            self.listLock.release() # release the list
            
