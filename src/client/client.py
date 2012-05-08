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
        getData()
        self.__ui = UICollector()
        

    def getData(self):
        
        data = self.__socket.recv(CC.PACKETSIZE)
        

   
        

class UICollector(threading.Thread):    
