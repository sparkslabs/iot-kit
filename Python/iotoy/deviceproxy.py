#!/usr/bin/python

import os, select, time, pprint
import serial

class serial_io(object):
    serialport = '/dev/ttyUSB2'
    baudrate = 9600
    def __init__(self, serialport=None, baudrate=None, dotimeout=True):
        if serialport:
            self.serialport = serialport
        if baudrate:
            self.baudrate = baudrate
        self.ser = serial.Serial(self.serialport, self.baudrate, timeout=1)
        self.ser.setTimeout(2)
        self.dotimeout = dotimeout
        self.inbuffer =  ""
    #
    def recv(self):
        acttime = time.time()
        while True:
            if time.time() - acttime > 2:
                if self.dotimeout:
                    raise Exception("timeout_waiting")
            if self.ser.inWaiting() >0:
                c = self.ser.read()
                if c:
                    acttime = time.time()
                    self.inbuffer += c
                    while self.inbuffer.find("\r\n") != -1:
                        chopped_line = self.inbuffer[:self.inbuffer.find("\r\n")]
                        self.inbuffer = self.inbuffer[self.inbuffer.find("\r\n")+2:]
                        return chopped_line
                else:
                    if self.dotimeout:
                        raise Exception("timeout_character")
    #
    def send(self, data, newline=True):
        self.ser.write(data)
        if newline:
            self.ser.write("\n")
    #
    def send_recv(self, data):
        self.send(data)
        return self.recv()
    #
    def call(self, data):
        result = self.send_recv(data)
        return parse_hostline(result)

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

        self.funcs[name] = { "value" :{ "name" : funcname,
                                        "spec" : { "args": args,
                                                   "result": result },
                                        "help" : funchelp }
                           }

    def __repr__(self):
        return pprint.pformat(self.devinfo(), width=132)

    def devinfo(self):
        return {"devicename" : self.name,
                "funcs" : self.funcs,
                "attrs" : self.attrs}

    def introspect_device(self):
        startline = self.device.recv() # Initial startline may fail - eg device was connected some time beforehand
        code, message, data = parse_hostline(startline)

        if code == 200:
            self.set_name(data)

        code, message, funclist  = self.device.call("funcs")
        code, message, attrlist  = self.device.call("attrs")

        self.configure_funclist(funclist)
        self.configure_attrlist(attrlist)

        for name in self.funcs.keys():
            code, message, funcsig  = self.device.call("help %s" % name)
            self.configure_func(name, funcsig)

        for name in self.attrs.keys():
            code, message, attrsig = self.device.call("help %s" % name)
            if code == 200:
                attrhelp = attrsig[attrsig.find(" - ")+3:]
                attrtype = attrsig[:attrsig.find(" - ")]

                self.attrs[name]["help"] = attrhelp
                # print "attr", name, "assert", self.attrs[name]["type"], "==", attrtype
                assert self.attrs[name]["type"] == attrtype

            # print "attrsig", name, attrsig
            #self.configure_func(name, funcsig)

    def __getattribute__(self, name):
        if (name in ["__repr__", "devinfo", "introspect_device", "configure_func",
                     "configure_attrlist", "configure_funclist", "set_name", "__init__",
                     "name", "funcs", "attrs", "device"]):
            x = super(DeviceProxy, self).__getattribute__(name)
            return x
        else:
            if name in self.funcs.keys():
                if len(self.funcs[name]["value"]["spec"]["args"])==0:
                    if len(self.funcs[name]["value"]["spec"]["result"])==1:
                        resultname, resulttype = self.funcs[name]["value"]["spec"]["result"][0]
                    else:
                        resultname, resulttype = None, None

                    def function_proxy():
                        code, message, result = self.device.call("%s" % name)
                        if resulttype != None:
                            if resulttype == "int":
                                result = int(result)

                            if resulttype == "bool":
                                result = True if result == "True" else False

                            if resulttype == "float":
                                result = float(result)
                        return result

                elif len(self.funcs[name]["value"]["spec"]["args"])==1:
                    argname, argtype = self.funcs[name]["value"]["spec"]["args"][0]
                    if len(self.funcs[name]["value"]["spec"]["result"])==1:
                        resultname, resulttype = self.funcs[name]["value"]["spec"]["result"][0]
                    else:
                        resultname, resulttype = None, None

                    def function_proxy(arg):
                        if argtype == "int" and arg.__class__ != int:
                            raise ValueError("Should be int, recieved %s" % arg.__class__.__name__)

                        if argtype == "bool" and arg.__class__ != bool:
                            raise ValueError("Should be bool, recieved %s" % arg.__class__.__name__)

                        if argtype == "str" and arg.__class__ != str:
                            raise ValueError("Should be str, recieved %s" % arg.__class__.__name__)

                        if argtype == "float" and arg.__class__ != float:
                            raise ValueError("Should be float, recieved %s" % arg.__class__.__name__)

                        callspec = "%s %s" % (name, str(arg))
                        code, message, result = self.device.call(callspec)
                        if resulttype != None:
                            if resulttype == "int":
                                result = int(result)

                            if resulttype == "bool" and result.__class__ != bool:
                                result = True if value == "True" else False

                            if resulttype == "float":
                                result = float(result)

                        return result
                else:
                    raise ValueError("Don't really understand the calling spec")

                function_proxy.func_name = "%s_Proxy" % name
                return function_proxy

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

if __name__ == "__main__":
    print "This code does not have an internal diagnostic. See the examples"
    print "directory for one"
