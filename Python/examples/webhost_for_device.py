#!/usr/bin/python
"""

Create a web interface for a stdio based command host - examples:

    * ./webhost_for_device.py ../../Arduino/libraries/IOToy/examples/BotHostTiny/build-stdio/BotHostStdio
    * ./webhost_for_device.py ../../Arduino/libraries/IOToy/examples/TestHostTiny/build-stdio/TestHostStdio

"""
import os
import sys
import pprint
import json
import time

from iotoy.deviceproxy import commandio, DeviceProxy
from iotoy.webinterface import webserver_started, DeviceWebInterface

default_host = "../../Arduino/libraries/IOToy/examples/TestHostTiny/build-stdio/TestHostStdio"

if len(sys.argv) == 1:
    host = default_host
else:
    host = sys.argv[1]

try:
    os.stat(host)
except OSError:
    print "=================================================================="
    print
    print "  For this to work, you need to build the example:"
    print host
    print
    print "eg:"
    print
    print "cd ./libraries/IOToy/examples/TestHostTiny/"
    print "make -f Makefile_mock"
    print
    print "(Change this to match your command host)"
    print 
    print "=================================================================="
    raise

io = commandio(host)
proxy = DeviceProxy(device=io)
proxy.introspect_device()

dev_interface = DeviceWebInterface(proxy)
dev_interface.start()

dev_interface.wait_server_start()

print "Device ready"

# Wait for the web interface thread to exit
while True:
    time.sleep(1)
