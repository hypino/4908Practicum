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
ClientAdder

"""

import socket
import threading

import ClientHandlerConstants as CHC

class ClientAddr(threading.Thread):
    
    def __init__(self, clientSocket, clientList, clientListLock, dbLock):
            threading.Thread.__init__(self, name='client_addition_thread')
            
            self.__clientSocket = clientSocket
            self.__clientList = clientList
            self.__listLock = clientListLock 
            self.__dbLock =  dbLock
	    self.run()
            
    def run(self):
        
	# read history from pytable and send to new client	

	# while still reading the db 
		# self.dbLock.acquire()
		# data = read hunk from database 
		# self.clientSocket.send(data)
		# self.dbLock.release()
 
        self.clientListLock.acquire()  # attempt to gain access to the client list
        self.clientList.append(self.clientSocket)
        self.clientListLock.release()
        
