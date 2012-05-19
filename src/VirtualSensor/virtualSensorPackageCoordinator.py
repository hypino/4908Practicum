#!/usr/bin/python
# -*- coding: latin-1 -*-

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

'''Virtual Sensor Package Coordinator'''

__revision__ = "$Rev: 4190 $"
# $Id: virtualSensorPackageCoordinator.py 4190 2012-04-26 23:03:04Z dave $

import time
import Queue
import threading
import signal
import optparse
import os
import sys

from virtualSensorPackageStaticValue import VSPStaticValuesTCPServer, VSPStaticValuesLogic
from virtualSensorPackageSignalGenerator import VSPSignalGeneratorTCPServer, VSPSignalGeneratorLogic

import virtualSensorPackageConstants as vspc

def signalHandler(signal, frame):
    try:
        print "\n"
        os.kill(os.getpid(), 9)
    except:
        print "\n -----virtualSensor termination failed-----"
        exit(1)

class VirtualSensorPackageCoordinator(threading.Thread):
    '''
    Thread to start/monitor rpc/logic threads when requested.

    '''

    def __init__(self, requestQueue, startPort=56001, udpPort=57002):
        threading.Thread.__init__(self, name='coordinator_thread')

        self.requestQueue = requestQueue
        self.udpPort = udpPort

        self.currentPort = startPort
        self.currentSerial = 1

        self.keepRunning = True

        self.start()

    def run(self):
        while self.keepRunning:
            # check for new VSP requests
            while not self.requestQueue.empty():
                item = self.requestQueue.get()

                if item[0] == vspc.REQUEST_CREATE_VSP:
                    self.createVSP(item[1], item[2])

            time.sleep(1)

    def shutdown(self):
        self.keepRunnig = False

    def createVSP(self, vspType, logInterval):

        dataQueue = Queue.Queue()     # used to pass data from Logic thread to RPC thread
        commandQueue = Queue.Queue()  # used to issue commands from the RPC thread to the Logic thread

        if vspType == vspc.VSP_STATIC:

            newTCPServer = VSPStaticValuesTCPServer(dataQueue, commandQueue,
                                                    self.currentPort, self.currentSerial)
            newLogic = VSPStaticValuesLogic(dataQueue, commandQueue,
                                            self.currentPort, self.currentSerial,
                                            self.udpPort, logInterval)
            print "Creating staticValue VSP '%s' on port %d with log interval: %0.3fsec" % (self.currentSerial, self.currentPort, logInterval)

        elif vspType == vspc.VSP_SIGNAL_GENERATOR:

            newTCPServer = VSPSignalGeneratorTCPServer(dataQueue, commandQueue,
                                                       self.currentPort, self.currentSerial)
            newLogic = VSPSignalGeneratorLogic(dataQueue, commandQueue,
                                               self.currentPort, self.currentSerial,
                                               self.udpPort, logInterval)
            print "Creating signalGenerator VSP '%s' on port %d with log interval: %0.3fsec" % (self.currentSerial, self.currentPort, logInterval)

        else:
            return

        self.currentSerial += 1
        self.currentPort += 1


def MainLoop():
    '''
    Main program loop, which creates a VSPCoordinator and then requests the creation of
    VSPs as per the command-line inputs.

    '''
    signal.signal(signal.SIGINT, signalHandler)

    opts = optparse.OptionParser()

    opts.add_option('-n', '--nSensors', action="store", type="int", dest='nSensors',
                    help='number of virtual sensor packages to create', default=20)

    opts.add_option('-i', '--interval', action="store", type="float", dest='interval',
                    help='interval between logged data entries (seconds)', default=0.01)

    opts.add_option('-p', '--port', action="store", type="int", dest='port',
                    help='starting port when creating virtual sensor packages', default=56001)

    opts.add_option('-u', '--udpport', action="store", type="int", dest='udpPort',
                    help='port used to send UDP pings', default=57002)

    (options, arguments) = opts.parse_args()

    requestQueue = Queue.Queue()
    coordinator = VirtualSensorPackageCoordinator(requestQueue, options.port, options.udpPort)

    print "Starting VSP Coordinator"
    print "UDP ping port: %d" % options.udpPort

    # create specified number of VSPs
    for index in range(options.nSensors):
        print "Queuing creation of VSP #%d" % (index+1)
        requestQueue.put([vspc.REQUEST_CREATE_VSP, vspc.VSP_SIGNAL_GENERATOR, options.interval])

    # run forever
    print "Running forever..."
    while True:
        pass


if __name__ == '__main__':
    MainLoop()
