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
    
    def getSocket(self):
        return self.__socket
    
    """Implemented fileno so that a sensor
    object can be treated like a file descriptor,
    which is essentially what it is with more
    data.
    
    The "select" function call requires that
    the list of objects that it is polling
    has a fileno method that returns an integer
    representing the identity of the file
    descriptor.
    
    """
    def fileno(self):
        return self.__socket.fileno()    