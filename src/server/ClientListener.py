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
import ClientAdder
import ClientServer

"""
This class listens on a TCP port for client connections and accepts the connection.  It then creates 
an instance of ClientAdder, which updates the new client's data, adds the client to the list of connected clients
"""

class ClientListener():
    
    def __init__(self):
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.bind((CHC.HOST, CHC.LISTENPORT))
        self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listLock = threading.Semaphore()
        clientServer = ClientServer(clientList, self.listLock)
        self.clienList = []
        clientServer.run()
    
    def listen():
        while(1):
            self.listenSocket.listen(5) #allows for a backlog of 5 sockets
            newSock, newAdd = self.listenSocket.accept()
            newSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            adder = ClientAdder(newSock, self.clientList, self.listLock)
            adder.run()
            