#--------------------------------------------------------------------------------------------
#--	SOURCE FILE:	serverMain.py    - Collects Data from sensors and save/process them.
#--											  
#--	PROGRAM:	SensorServer
#--
#--	FUNCTIONS:		
#--						
#--	DATE:		April 30, 2012	
#--
#--	REVISIONS:	1.0
#--
#--	DESIGNER:	Mike Zobac, Chris Sim, Tyler Allison
#--
#--	PROGRAMMER	Mike Zobac, Chris Sim, Tyler Allison
#--
#--	NOTES:		
#--
#--------------------------------------------------------------------------------------------

import sys
import select, socket
import os
import time
import Queue
import threading
import argparse
import signal

from ClientHandlerConstants import *
from database import DataHandler
import Sensor as s
import ClientListener as cl
from SensorDataCollector import SensorDataCollector

# broadcasting IP and port
addr = ("0.0.0.0", 57002)
# 2 bytes serial number + 2 bytes port number
bufsize = 4
# list of sensors registered on server
sensorList = []

def signalHandler(signal, frame):
    print "Server Terminating Safely..."
    os.kill(int(os.getpid()), 9)    
        
# main thread
def Main():
    
    signal.signal(signal.SIGINT, signalHandler)
    db = DataHandler()    

    print "server running..."
    
    # command-line arguments handling for options goes here
    
    # forking a process that handles clients
    
    child_pid = os.fork()
    if child_pid == 0:  #  CHANGE THIS BACK FOR THE LOVE OF GOD!!!!!!!!
        print "Client Listener process created, PID# %s" % os.getpid()  
        clientHandler = cl.ClientListener(db)
    else:
        print "Main process PID# %s" % os.getpid()    
    
    # creating Tyler's thread
    sdc = SensorDataCollector(sensorList, db)
    
    # creating UDP listening socket
    listenSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listenSock.bind(addr)
    # non blocking socket
    listenSock.setblocking(0)

    # listening and receiving broadcast datagrams
    while True:
        # same as what we did in Linux chat assignment
        result = select.select([listenSock],[],[])
        try:
            sensorExist = False
            
            # recvfrom returns string data and sender's IP
            data, sensorIP = result[0][0].recvfrom(bufsize)
            
            # save packet data here
            serialNum = ord(data[0])
            port = ord(data[2]) + ord(data[3]) * 16**2
            
            # check serial num here
            # if it's in the list, continue  
            if(len(sensorList) != 0):    
                for i in sensorList:
                    serialOld = i.getSerial()
                    if serialNum == i.getSerial():
                        sensorExist = True
                        break
                if(sensorExist == True):
                    continue
            
            # if not, add to the list    
            # create TCP Socket            
            dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #connect
            dataSock.connect((sensorIP[0], port))
            newSensor = s.Sensor(serialNum, dataSock)                 
            sensorList.append(newSensor)
            if len(sensorList) > 20:
                HISTORYSIZE = len(sensorList) * 100
            print "Sensor %d found" % serialNum        
        
            # Send START msg
            dataSock.send(bytes(CONTROL_COMMAND_START))
            dataSock.send(bytes(CONTROL_COMMAND_GIVE))
            # close the socket
            
        except socket.error:
            print "Error occurred"
            listenSock.close()
            break
        

if __name__ == '__main__':
    Main()
