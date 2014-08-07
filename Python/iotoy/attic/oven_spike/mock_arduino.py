#!/usr/bin/python

import threading
import time

######################################################################
#
# ARDUINO MOCK CODE - for testing the high level code without needing Hardware
#
######################################################################

class MockArduino_OvenHost(threading.Thread):
    # Well, obviously not a "real" oven, simulation of an oven
    """This simulates an oven that we're communicating with over
    a serial connection. In particular, it simulates what we're
    communicating to. If there was an arduino on the system, this
    would be the arduino part"""
    daemon = True

    def __init__(self, fake_serial):
        super(MockArduino_OvenHost, self).__init__()
        self.fake_serial = fake_serial
        self._temp = 20
        self._target = 20

    def simulate_tick(self):
            if self._temp < self._target:
                if (self._target - self._temp) > 30:
                    self._temp += 15
                else:
                    self._temp = int((self._temp + self._target) / 2.0 + 0.5)
            if self._temp > self._target:
                self._temp = int((self._temp + self._target) / 2.0)

    def run(self):
        start = last = time.time()
        while True:
            now = time.time()
            if now - last > 0.5:
                self.simulate_tick()
                last = now
            raw_command = self.fake_serial.read()

            if raw_command:
                command = raw_command.split()
                if command[0] == "HELP":
                    self.fake_serial.write("HELP NOT YET IMPLEMENTED\n")
                if command[0] == "GET":
                    if command[1] == "temp":
                        self.fake_serial.write(str(self._temp) + "\n")
                    elif command[1] == "target":
                        self.fake_serial.write(str(self._target) + "\n")
                    else:
                        self.fake_serial.write("UNKNOWN GET")

                if command[0] == "SET":
                    if command[1] == "target":
                        self._target = int(command[2])
                        #self.fake_serial.write("200 target ")
                        self.fake_serial.write(str(self._target) + "\n")
                    else:
                        self.fake_serial.write("UNSUPPORTED SET")

            time.sleep(0.01)
