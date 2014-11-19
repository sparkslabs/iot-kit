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

from iotoy.deviceproxy import serial_io, DeviceProxy
from iotoy.webinterface import webserver_started, DeviceWebInterface
from iotoy.discovery import IOTWebService

io = serial_io("/dev/ttyACM0", 19200, debug=False)

proxy = DeviceProxy(device=io)
proxy.introspect_device()

dev_interface = DeviceWebInterface(proxy)
dev_interface.start()

dev_interface.wait_server_start()
iotservice = IOTWebService(name=proxy.name)
iotservice.start()
iotservice.wait_advertised()

print "Device ready - look for %s._iotoy._tcp.local via avahi-browse -r -a" % proxy.name

# Wait for the web interface thread to exit
while True:
    time.sleep(1)
