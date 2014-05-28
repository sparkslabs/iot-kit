#!/usr/bin/python

import os, select, time

class commandio(object):
    def __init__(self, command):
        self.command = command
        self._send, self._recv = os.popen2(self.command)

    def recv(self):
        time.sleep(0.01)
        r,w,e = select.select([self._recv], [self._send], [])
        if self._recv not in r:
            raise Exception("Bad Device")
        line = self._recv.readline()
        return line

    def send(self, data):
        self._send.write(data + "\n")
        self._send.flush()

try:
    os.stat("./libraries/IOToy/examples/BotHostTiny/build-stdio/BotHostStdio")
except OSError:
    print "=================================================================="
    print
    print "  You need to build the BotHostStdio example for this to work..."
    print
    print "cd ./libraries/IOToy/examples/BotHostTiny/"
    print "make -f Makefile_mock"
    print
    print "=================================================================="
    raise

io = commandio("./libraries/IOToy/examples/BotHostTiny/build-stdio/BotHostStdio")

startline = io.recv()
print startline

for data in ["help", "help help", "funcs", "attrs"]:
    io.send(data)
    line = io.recv()
    print data, (20-len(data))*" ", "--> :", repr(line)
