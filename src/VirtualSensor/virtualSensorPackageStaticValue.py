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

''' Virtual Sensor Package (Static Value)'''

__revision__ = "$Rev: 4189 $"
# $Id: virtualSensorPackageStaticValue.py 4189 2012-04-26 22:47:48Z dave $

import time

import virtualSensorPackageConstants as vspc
from virtualSensorPackagePrototypes import VirtualSensorPackageTCPServerPrototype, VirtualSensorPackageLogicPrototype

class VSPStaticValuesTCPServer(VirtualSensorPackageTCPServerPrototype):
    def __init__(self, dataQueue, commandQueue,
                 port, serialNumber):
        VirtualSensorPackageTCPServerPrototype.__init__(self, dataQueue, commandQueue,
                                                        port, serialNumber)

class VSPStaticValuesLogic(VirtualSensorPackageLogicPrototype):
    def __init__(self, dataQueue, commandQueue, statusQueue, controlQueue,
                 port, serialNumber, udpPort, logInterval):
        VirtualSensorPackageLogicPrototype.__init__(self, dataQueue, commandQueue,
                                                    port, serialNumber, udpPort, logInterval)

        self._staticValue = 1 # the static value to return

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

                timeSec = int(self._lastLogTime)
                timeMS = int((timeSec - self._lastLogTime) * 1000.0)

                # dataLine is: time (sec), time (ms), dataCols (8)
                self._dataQueue.put([timeSec, timeMS,
                                     self._staticValue, self._staticValue,
                                     self._staticValue, self._staticValue,
                                     self._staticValue, self._staticValue,
                                     self._staticValue, self._staticValue])

