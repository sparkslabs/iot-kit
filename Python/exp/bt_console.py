#!/usr/bin/python

import serial
import sys

bluetoothSerial = serial.Serial( "/dev/rfcomm0", baudrate=9600 )

while True:

    command = raw_input(">>> ")
    bluetoothSerial.write( command +"\n")

    while bluetoothSerial.inWaiting() > 0:
       sys.stderr.write(bluetoothSerial.read(1))
       sys.stderr.flush()

