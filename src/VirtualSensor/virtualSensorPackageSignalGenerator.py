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

''' Virtual Sensor Package (Signal Generator)'''

__revision__ = "$Rev: 4189 $"
# $Id: virtualSensorPackageSignalGenerator.py 4189 2012-04-26 22:47:48Z dave $

import time
import math

import virtualSensorPackageConstants as vspc
from virtualSensorPackagePrototypes import VirtualSensorPackageTCPServerPrototype, VirtualSensorPackageLogicPrototype

class VSPSignalGeneratorTCPServer(VirtualSensorPackageTCPServerPrototype):
    def __init__(self, dataQueue, commandQueue, port, serialNumber):
        VirtualSensorPackageTCPServerPrototype.__init__(self, dataQueue, commandQueue,
                                                        port, serialNumber)

class VSPSignalGeneratorLogic(VirtualSensorPackageLogicPrototype):
    def __init__(self, dataQueue, commandQueue,
                 port, serialNumber, udpPort, logInterval):
        VirtualSensorPackageLogicPrototype.__init__(self, dataQueue, commandQueue,
                                                    port, serialNumber, udpPort, logInterval)

        self._amplitude = 1
        self._frequency = 0.25
        self._offset = 0
        self._shift = 0

    def updateData(self):

        currentTime = int(time.time())

        if currentTime - self._lastLogTime >= self._logInterval:
            # Log points AT logInterval spacing, don't assume this routine will
            #  be called quickly enough to occur ON the interval edges.
            if self._isLogging:
                if self._lastLogTime == 0:
                    self._lastLogTime = currentTime
                else:
                    self._lastLogTime += self._logInterval

                signalValue = math.sin((self._lastLogTime * self._frequency) + self._shift) * self._amplitude + self._offset

                timeSec = int(self._lastLogTime)
                timeMS = int((self._lastLogTime - timeSec) * 1000.0)

                # dataLine is: time (sec), time (ms), dataCols (8)
                self._dataQueue.put([timeSec, timeMS,
                                     signalValue, signalValue,
                                     signalValue, signalValue,
                                     signalValue, signalValue,
                                     signalValue, signalValue])

