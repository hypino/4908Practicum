class Sensor(object):
    
    def __init__(self, serialNumber, socket):
        self.__serialNumber = serialNumber
        self.__socket = socket
        
    def getSerial(self):
        return self.__serialNumber
    
    def fileno():
        return self.__socket.fileno()