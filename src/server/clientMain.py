from client import Client
import clientConstants as CC
import signal


host = "192.168.0.3"
client = Client(host)

def signalHandler(signal, frame):        
        print "Stoped!"
        client.shutdown()
        exit(0)

def Main():
	
    signal.signal(signal.SIGINT, signalHandler)
    print "Client Running"
    host = "192.168.0.3"
    client.getHistory()
	

if __name__ == '__main__':
    Main()	





