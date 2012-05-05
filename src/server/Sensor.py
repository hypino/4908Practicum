'''Data object purely for keeping all sensor-related
information in one place.

Contains the serial number and the socket associated
with this sensor.

Also has a fileno method so that it is compatible
with the select statement. In other words, this
object can be treated like a file descriptor.

Author: Tyler Allison
'''
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