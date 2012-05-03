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
    
    def __init__(self, clientSocket, clientList, listLock):
            threading.Thread.__init__(self, name='client_addition_thread')
            
            self.clientSocket = clientSocket
            self.clientList = clientList
            self.listLock = listLock
            self.controlSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.controlSocket.bind((CHC.LISTENPORT, CHC.COMMPORT))
            self.controlSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)            
            
    def run(self):
        
        self.controlSocket.send(CHC.CONTROL_COMMAND_STOP)
        self.controlSocket.rec(1) # wait for return message from select thread
        
        # Send read history from pytable and send to new client
        
        self.listLock.acquire()  # attempt to gain access to the client list
        self.clientList.append(self.clientSocket)
        self.listLock.release()
        self.controlSocket.send(CHC.CONTROL_COMMAND_GIVE)