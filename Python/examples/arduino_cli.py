#!/usr/bin/python


from iotoy.deviceproxy import serial_io
import time
import sys

port = serial_io("/dev/ttyUSB4", 19200)
for i in "wait":
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(1)
sys.stdout.write("\n")
sys.stdout.flush()

try:
    startline = port.recv()
except:
    print "Initialisation failed badly"
else:
    print "Arduino CLI V0.0 (Aug 2014)"
    print "Connected to /dev/ttyUSB2"
    print "To find out what the device does, type 'help'."
    print "Basic device info:"
    print "                  ", startline

while True:
    line = raw_input(">>> ")
    line = line.strip()
    port.send(line)
    try:
        response = port.recv()
    except:
        pass
    else:
        print response
