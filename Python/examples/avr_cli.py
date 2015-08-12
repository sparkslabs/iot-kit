#!/usr/bin/python


from iotoy.deviceproxy import serial_io
import time
import sys

port = None
for dev in ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2"]:
    try:
        port = serial_io(dev, 19200)
        break
    except OSError:
        pass

if port == None:
    sys.exit(1)

print dev
for i in "wait":
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(1)
sys.stdout.write("\n")
sys.stdout.flush()

try:
    startline = port.recv()
except:
    print "Type devinfo"
    print
    startline = ""

print "Arduino CLI V0.0 (Aug 2014)"
print "Connected to", dev
print "To find out what the device does, type 'help'."
if startline:
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
