class Sensor(object):
    
    def __init__(self, serialNumber, socket):
        self.__serialNumber = serialNumber
        self.__socket = socket
        
    def getSerial(self):
        return self.__serialNumber
    
    def fileno(self):
        return self.__socket.fileno()
    
    def getSocket(self):
        return self.__socket