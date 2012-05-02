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

from sys import *
import select, socket
import time
import Queue
import threading
import argparse
import Sensor as s

# broadcasting IP and port
addr = ("0.0.0.0", 57002)
# 2 bytes serial number + 2 bytes port number
bufsize = 4
# list of sensors registered on server
sensorList = []
# start message
startMSG = "00"

# Tyler's thread
class SelectThread(threading.Thread):
    def __init__():
        threading.Thread.__init__()
        
# main thread
def Main():
    print "server running..."
    
    # command-line arguments handling for options goes here
    
    # creating Tyler's thread
    #st = SelectThread()
    
    # creating UDP listening socket
    listenSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            newSensor = s.Sensor(serialNum, dataSock)                 
            sensorList.append(newSensor)
            print "Sensor %d found" % serialNum        
            
            # debugging code - printing the sensors in the list
            #for j in sensorList:
            #    print j.getSerial()
            #print "---"

            # Connect
            dataSock.connect((sensorIP[0], port))
            # Send START msg
            dataSock.send(startMSG)
            dataSock.close()
            
        except socket.error:
            print "Error occured"
            listenSock.close()
            break
        

if __name__ == '__main__':
    Main()
    
