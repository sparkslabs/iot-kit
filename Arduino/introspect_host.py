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
    def __init__(self,device=None):
        self.name = None
        self.funcs = {}
        self.attrs = {}
        self.device = device

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
        return pprint.pformat(self.devinfo(), width=132)

    def devinfo(self):
        return {"devicename" : self.name,
                "funcs" : self.funcs,
                "attrs" : self.attrs}

    def introspect_device(self):
        startline = io.recv() # Initial startline may fail - eg device was connected some time beforehand
        code, message, data = parse_hostline(startline)

        if code == 200:
            self.set_name(data)

        code, message, funclist  = io.call("funcs")
        code, message, attrlist  = io.call("attrs")

        self.configure_funclist(funclist)
        self.configure_attrlist(attrlist)

        for name in self.funcs.keys():
            code, message, funcsig  = io.call("help %s" % name)
            self.configure_func(name, funcsig)

    def __getattribute__(self, name):
        if (name in ["__repr__", "devinfo", "introspect_device", "configure_func",
                     "configure_attrlist", "configure_funclist", "set_name", "__init__",
                     "name", "funcs", "attrs", "device"]):
            x = super(DeviceProxy, self).__getattribute__(name)
            return x
        else:
            if name in self.funcs.keys():
                return "wibble"
            elif name in self.attrs.keys():
                code, code_message, value = self.device.call("get %s" % name)
                if code != 200:
                    raise AttributeError("Cannot get %s, because %s" % (name, code_message))
                if self.attrs[name]["type"] == "int":
                    value = int(value)
                if self.attrs[name]["type"] == "float":
                    value = float(value)
                if self.attrs[name]["type"] == "bool":
                    if value == "True":
                        value = True
                    elif value == "False":
                        value = False
                    else:
                        raise ValueError("Bool values MUST be 'True' or 'False'")
                    value = True if value == "True" else False
                return value
            else:
                super(DeviceProxy, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if (name in ["__repr__", "devinfo", "introspect_device", "configure_func",
                     "configure_attrlist", "configure_funclist", "set_name", "__init__",
                     "name", "funcs", "attrs", "device"]):
            x = super(DeviceProxy, self).__setattr__(name,value)
            return x
        else:
            if name in self.funcs.keys():
                raise ValueError("Cannot Set Function value")
            elif name in self.attrs.keys():
                if self.attrs[name]["type"] == "int":
                    if value.__class__ != int:
                        raise ValueError("%s is an int, but you provided %s which is %s" % (name, repr(value), repr(value.__class__.__name__) ) )

                if self.attrs[name]["type"] == "float":
                    if value.__class__ != float:
                        raise ValueError("%s is a float, but you provided %s which is %s" % (name, repr(value), repr(value.__class__.__name__) ) )

                if self.attrs[name]["type"] == "str":
                    if value.__class__ != str:
                        raise ValueError("%s is a str, but you provided %s which is %s" % (name, repr(value), repr(value.__class__.__name__) ) )

                if self.attrs[name]["type"] == "bool":
                    if value.__class__ != bool:
                        raise ValueError("%s is a bool, but you provided %s which is %s" % (name, repr(value), repr(value.__class__.__name__) ) )

                result = self.device.call("set %s %s" % (name, str(value)) )
                return result
            else:
                super(DeviceProxy, self).__getattribute__(name)

io = commandio(default_host)
p = DeviceProxy(device=io)
p.introspect_device()

print p

print

print "p.drive_forward_time_ms", repr(p.drive_forward_time_ms)
p.drive_forward_time_ms = 1000
print "p.drive_forward_time_ms", repr(p.drive_forward_time_ms)
assert p.drive_forward_time_ms == 1000

print

print "p.turn_time_ms", repr(p.turn_time_ms)
p.turn_time_ms = 500
print "p.turn_time_ms", repr(p.turn_time_ms)

assert p.turn_time_ms == 500

try:
    p.turn_time_ms = True
except ValueError as e:
    assert e.message == "turn_time_ms is an int, but you provided True which is 'bool'"
    print "Successfully caught attempt to put a bool into an int"

try:
    p.turn_time_ms = 1.1
except ValueError as e:
    if e.message != "turn_time_ms is an int, but you provided 1.1 which is 'float'":
        raise e
    print "Successfully caught attempt to put a float into an int"

try:
    p.turn_time_ms = 'hello'
except ValueError as e:
    if e.message != "turn_time_ms is an int, but you provided 'hello' which is 'str'":
        raise e
    print "Successfully caught attempt to put a str into an int"
