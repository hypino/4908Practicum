#!/usr/bin/env python
# -*- coding: latin-1 -*-

#
# BCIT COMP 4908 Practicum for
# Convergent Manufacturing Technologies Inc.
# 6190 Agronomy Road, Suite 403
# Vancouver, British Columbia, Canada
# support@convergent.ca  or http://www.convergent.ca
#
#
# Tyler Alison, Chris Sim, Mike Zobac
# 

"""
ClientHandler Constants

"""

#select constants
SELECT_TIMEOUT = 0.1

# control commands
CONTROL_COMMAND_START = 0
CONTROL_COMMAND_STOP = 1
CONTROL_COMMAND_GIVE = 2

#TCP Socket Constants

HOST = ''
LOCALHOST = '127.0.0.1'
LISTENPORT = 4908
DATAPORT = 51011

DATASIZE = 70
CLIENT_PACKET_SIZE = 9

#local data folder
LOCALDATA = "/usr/temp"