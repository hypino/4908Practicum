#!/usr/bin/env python

#
# Convergent Manufacturing Technologies Inc.
# 6190 Agronomy Road, Suite 403
# Vancouver, British Columbia, Canada
# support@convergent.ca  or http://www.convergent.ca
#
#
# (c)2012 Convergent Manufacturing Technologies, Inc
# All rights reserved.
#

''' Virtual Sensor Package Prototypes'''

__revision__ = "$Rev: 4189 $"
# $Id: virtualSensorPackagePrototypes.py 4189 2012-04-26 22:47:48Z dave $

import SocketServer
import threading
import time
import socket
import struct


import virtualSensorPackageConstants as vspc

PING_SEND_DELAY = 10 # contact time before a node starts sending pings again (seconds)
DEFAULT_LOG_INTERVAL = 0.05 # seconds between logged data points


class VirtualSensorPackageTCPServerPrototype(threading.Thread):
    '''
    Prototype for VSP TCPServers.

    '''
    def __init__(self, dataQueue, commandQueue,
                 port, serialNumber):
        threading.Thread.__init__(self, name='vsp_tcp')

        self._tcpServer = SocketServer.TCPServer(('', port), MyTCPHandler)

        # add some additional attributes to the TCP server
        self._tcpServer.dataQueue = dataQueue
        self._tcpServer.commandQueue = commandQueue
        self._tcpServer.dataList = []

        self.start()

    def run(self):
        while True:
            self._tcpServer.handle_request()

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    Custom handler to process VSP control command messages.

    """
    def handle(self):
        # try/except used to deal with data not being ready yet on a non-blocking socket
        self.data = None
        while self.data is None:
            try:
                self.data = self.request.recv(1024)
            except socket.timeout:
                pass
            except socket.error:
                return

        if len(self.data) == 0:
            return

        packedResult = '\x00' # default return value, if result of call is False

        controlByte = struct.unpack('<B', self.data[0])[0]

        # split up the control byte
        controlCommand = controlByte & 0x03
        throttleValue = (controlByte & 0xFC) >> 2

        if controlCommand == vspc.CONTROL_COMMAND_START:
            self.server.commandQueue.put([vspc.SET_IS_LOGGING, True])
            packedResult = '\x01'

        elif controlCommand == vspc.CONTROL_COMMAND_STOP:
            self.server.commandQueue.put([vspc.SET_IS_LOGGING, False])
            packedResult = '\x01'

        elif controlCommand == vspc.CONTROL_COMMAND_GIVE:

            # first pull any queued data
            while not self.server.dataQueue.empty():
                item = self.server.dataQueue.get()
                self.server.dataList.append(item)

            # prepare reply data
            if len(self.server.dataList) > 0:
                # determine how much data to send (based on the throttle value)
                nRows = len(self.server.dataList)
                while throttleValue > 0:
                    nRows = nRows >> 1
                    throttleValue = throttleValue >> 1

                structFormat = '<' + ('IHdddddddd') * nRows

                # combine all the rows to be struct packed
                allData = [item for sublist in self.server.dataList[:nRows] for item in sublist]

                packedResult = struct.pack(structFormat, *allData)

                # remove sent lines from the buffer
                self.server.dataList = self.server.dataList[nRows:]

            else:
                # no data to return
                pass
        else:
            # unknown control command
            pass


        # let the logic thread know that we processed a call
        self.server.commandQueue.put([vspc.ETHERNET_CONTACT])

        try:
            self.request.send(packedResult)
        except socket.error:
            # connection reset by peer
            pass


class VirtualSensorPackageLogicPrototype(threading.Thread):
    '''
    The VSP logic thread does only 3 things:
    - Send network UDP pings when necessary to keep the network 'alive'
    - Update local logging state flags based on messages from the TCP server
    - Add datalines to the dataQueue for the TCP thread to return when data is requested

    These are the only operations performed by a VSP that aren't direct reactions
    to external calls, which are all handled by the TCP server thread.

    '''
    def __init__(self, dataQueue, commandQueue,
                 port, serialNumber, udpPort, logInterval=DEFAULT_LOG_INTERVAL):
        threading.Thread.__init__(self, name='vep_logic')

        self._dataQueue = dataQueue        # used to pass dataLines to the RPC thread
        self._commandQueue = commandQueue  # used to set some values from the RPC thread

        self._port = port

        self._serialNumber = serialNumber
        self._udpPort = udpPort

        self._isLogging = False
        self._logInterval = logInterval

        # misc variables
        self._lastLogTime = 0
        self._lastEthernetContactTime = 0
        self._lastEthernetPingTime = 0

        self.keepRunning = True

        self.start()

    def run(self):

        # reset contact/ping time on startup
        self._lastEthernetContactTime = time.time() - PING_SEND_DELAY
        self._lastEthernetPingTime = self._lastEthernetContactTime

        # main logic loop
        while self.keepRunning:
            self.updateNetwork()
            self.processCommands()
            self.updateData()

            # avoid wasting CPU cycles
            time.sleep(0.0001) # this should be less than the smallest log interval (0.001sec)

    def shutdown(self):
        self.keepRunning = False

    def updateNetwork(self):

        # send UDP ping if the contact delay has ellapsed
        currentTime = time.time()
        if currentTime - self._lastEthernetContactTime >= PING_SEND_DELAY:
            if currentTime - self._lastEthernetPingTime >= PING_SEND_DELAY:
                self._lastEthernetPingTime = currentTime

                udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

                payload = struct.pack('<HH', self._serialNumber, self._port)

                # send UDP ping
                udpSock.sendto(payload, ('<broadcast>', self._udpPort))

                # linux doesn't require/handle this
                try:
                    udpSock.shutdown(2)
                except:
                    pass
                udpSock.close()


    def processCommands(self):
        if not self._commandQueue.empty():
            item = self._commandQueue.get()

            if item[0] == vspc.SET_IS_LOGGING:
                self._isLogging = item[1]
                # When logging is forced on, reset the last log time so new data
                #  shows up starting NOW, not since the last actual logged data.
                # Note: This may be better handled in the updateData of the sub-classed
                #  logic handlers.
                if self._isLogging:
                    self._lastLogTime = 0

            elif item[0] == vspc.ETHERNET_CONTACT:
                self._lastEthernetContactTime = time.time()


    def updateData(self):
        raise NotImplemented, 'updateData() not implmented'

