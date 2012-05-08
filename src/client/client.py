from tables import *
import numpy
import threading
from ../server/database import DataHandler

import clientConstants as CC

class Client():
    
    def __init__(self, host):
        
        self.__host = host        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind((CC.HOST, CC.LISTENPORT))
        self.__socket.connect((HOST, HOSTPORT))
        db = DataHandler()
        self.__dataCollector = DataCollector(self.__socket)
        self.__ui = UICollector()

class DataCollector(threading.Thread):
    
    def __init__(self, socket):
        
        self.__socket = socket
        self.run()

    def run(self):
        
        
        

class UICollector(threading.Thread):    
