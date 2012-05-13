from client import Client
import clientConstants as CC
import signal


def Main():
	
	host = "192.168.0.3"
	client = Client(host)
	signal.signal(signal.SIGINT, signalHandler)
	

if __name__ == '__main__':
    Main()	


def signalHandler(signal, frame):        
        print "Stoped!"
        exit(0)


