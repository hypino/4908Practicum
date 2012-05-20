from client import Client
import clientConstants as CC
import signal
import os


host = "192.168.0.3"
client = Client(host)

def signalHandler(signal, frame):        
        print "Client terminating safely..."
        exit(0)

def Main():
	
    signal.signal(signal.SIGINT, signalHandler)
    print "Client Running"
    host = "192.168.0.3"
    client.getHistory()
	

if __name__ == '__main__':
    Main()	





