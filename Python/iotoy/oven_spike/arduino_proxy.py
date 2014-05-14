#!/usr/bin/python

######################################################################
#
# SYSTEM PROXY - FOR INTERFACING WITH THE REAL OBJECT - EITHER DIRECTLY
# OR VIA SERIAL COMMS
#
######################################################################

class Oven(object):
    """\
    This is the local proxy for the physical device, that the
    network proxy uses to control the device"""
    daemon = True

    def __init__(self, ser):
        # Ser is the serial port we're using to communiate with
        # the IOT-able object
        self.ser = ser

    def get_targettemperature(self):
        """\
        This is the temperature that the oven is currently set
        to. This is always a target, not reality This could be a
        read-write property really
        """
        self.ser.write("GET target\n")
        result = self.ser.read()
        result = result.strip()
        result = int(result)
        return result

    def set_targettemperature(self, value):
        self.ser.write("SET target " + repr(value) + "\n")
        raw_result = self.ser.read()
        raw_result = raw_result.strip()
        result = raw_result.split()

    def temperature(self):
        """\
        This is the temperature that the oven currently is.
        You can't change this, just the target temp.
        """
        self.ser.write("GET temp\n")
        result = self.ser.read()
        result = result.strip()
        result = int(result)

        return result
