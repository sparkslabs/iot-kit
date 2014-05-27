#!/usr/bin/python

import os, select, time, pprint

default_host = "./libraries/IOToy/examples/TestHostTiny/build-stdio/TestHostStdio"

def parse_hostline(hostline):
    assert (hostline[-1] == "\n")
    hostline = hostline[:-1] # trim EOL
    statuscode = hostline[:hostline.find(":")]
    statuscode = int(statuscode)
    hostline = hostline[hostline.find(":")+1:]
    statusmessage = hostline[:hostline.find(":")]
    data = hostline[hostline.find(":")+1:]
    return (statuscode, statusmessage, data)

class commandio(object):
    def __init__(self, command):
        self.command = command
        self._send, self._recv = os.popen2(self.command)

    def recv(self):
        now = time.time()
        while True:
            r,w,e = select.select([self._recv], [self._send], [])
            time.sleep(0.01)
            if self._recv in r:
                break
            else:
                if time.time() - now > 1: # stdio device should definitely respond within 1 second
                    raise Exception("Bad Device")
        line = self._recv.readline()
        return line

    def send(self, data):
        self._send.write(data + "\n")
        self._send.flush()

    def send_recv(self, data):
        self.send(data)
        return self.recv()

    def call(self, data):
        result = self.send_recv(data)
        return parse_hostline(result)

try:
    os.stat("./libraries/IOToy/examples/TestHostTiny/build-stdio/TestHostStdio")
except OSError:
    print "=================================================================="
    print
    print "  You need to build the TestHostStdio example for this to work..."
    print
    print "cd ./libraries/IOToy/examples/TestHostTiny/"
    print "make -f Makefile_mock"
    print
    print "=================================================================="
    raise

class DeviceProxy(object):
    def __init__(self):
        self.name = None
        self.funcs = {}
        self.attrs = {}

    def set_name(self, name):
        self.name = name

    def configure_funclist(self, funclist):
        funcnames = funclist.split(",")
        for name in funcnames:
            self.funcs[name] = None

        # We don't provide these to clients of the proxy
        del self.funcs["devinfo"]
        del self.funcs["ping"]
        del self.funcs["help"]
        del self.funcs["funcs"]
        del self.funcs["attrs"]
        del self.funcs["set"]
        del self.funcs["get"]

    def configure_attrlist(self, attrlist):
        attrnames = attrlist.split(",")
        for attr in attrnames:
            name, typespec = attr.split(":")
            self.attrs[name] = { "type": typespec }

    def configure_func(self, name, funcsig):
        funcname = funcsig[:funcsig.find(" ")]
        funchelp = funcsig[funcsig.find(" - ")+3:]

        funcspec = funcsig[:funcsig.find(" - ")]
        funcspec = funcspec[funcspec.find(" ")+1:]
        if funcspec == "->":
            args = []
            result = []
        else:
            callsig, returnsig = funcspec.split("->")
            args = callsig.strip()
            result = returnsig.lstrip()
            if (" " in args) or (" " in result):
                args = "UNPARSED"
                result = "UNPARSED"
            else:
                parsed = args.split(":")
                if len(parsed) > 2:
                    parsed = "UNPARSED"
                elif len(args) == 0:
                    parsed = []
                else:
                    arg, argtype = parsed
                    parsed = [ (arg, argtype) ]
                args = parsed

                parsed = result.split(":")
                if len(parsed) > 2:
                    parsed = "UNPARSED"
                elif len(result) == 0:
                    parsed = []
                else:
                    arg, argtype = parsed
                    parsed = [ (arg, argtype) ]
                result = parsed

        self.funcs[name] = { "name" : funcname,
                             "spec" : { "args": args,
                                       "result": result },
                             "help" : funchelp
                           }

    def __repr__(self):
        return pprint.pformat({"devicename" : self.name,
                               "funcs" : self.funcs,
                               "attrs" : self.attrs})

    def device_spec(self):
        return {"devicename" : self.name,
                "funcs" : self.funcs,
                "attrs" : self.attrs}

io = commandio(default_host)

startline = io.recv()

code, message, data = parse_hostline(startline)

p = DeviceProxy()
if code == 200:
    p.set_name(data)

code, message, funclist  = io.call("funcs")
code, message, attrlist  = io.call("attrs")

p.configure_funclist(funclist)
p.configure_attrlist(attrlist)

for name in p.funcs.keys():
    code, message, funcsig  = io.call("help %s" % name)
    p.configure_func(name, funcsig)

pprint.pprint(p,width=200)
