from client import Client
import clientConstants as CC
import signal
import os
import sys



def signalHandler(signal, frame):        
        exit(0)

def Main():
	
    signal.signal(signal.SIGINT, signalHandler)
    print "Client Running"
    host = sys.argv[1]
    client = Client(host)
    client.getHistory()
	

if __name__ == '__main__':
    Main()	





