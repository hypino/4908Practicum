from client import Client
import clientConstants as CC
import signal


def signalHandler(signal, frame):        
        print "Stoped!"
        exit(0)

def Main():
	
    signal.signal(signal.SIGINT, signalHandler)
    host = "192.168.0.3"
    client = Client(host)
	

if __name__ == '__main__':
    Main()	





