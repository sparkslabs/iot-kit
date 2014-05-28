#!/usr/bin/python

import os
import pprint
import json
import time

import threading
import flask
from flask import request

from iotoy.deviceproxy import commandio, DeviceProxy

def webserver_started(port=5000):
    # This is really hacky, but there's no real workaround for this
    output = os.popen('netstat -nat').readlines()
    lines = [x.split()[3] for x in output if (x.startswith("tcp ") and ("LISTEN" in x) and (":5000" in x))]
    started = (len(lines) > 0 and lines[0].endswith(":5000"))
    return started

class DeviceWebInterface(threading.Thread):
    """Base class to assist with providing web APIs for IOT objects"""
    daemon = True

    # Thing attribute is provided as a utility for things that don't
    # want/need to provide a custom __init__ function
    def __init__(self, thing):
        threading.Thread.__init__(self)
        self.thing = thing
        self.ready = False
        self.app = None

    def wait_server_start(self, port=5000):
        while not webserver_started(port): # Avoid an annoying race hazard
            time.sleep(0.001)

    def run(self):
        self.devinfo = self.thing.devinfo()
        print self.thing
        self.app = app = flask.Flask(__name__)

        # Add the routes and methods for handling attributes
        # including appropriate data conversions/enforcement
        for attr in self.devinfo["attrs"]:
            attrtype = self.devinfo["attrs"][attr]["type"]
            self.devinfo["attrs"][attr]["href"] = "/"+attr
            self.devinfo["attrs"][attr]["methods"] = ["PUT","GET"]
            def handle_attr(attr=attr,attrtype=attrtype):
                global request
                try:
                    if request.method == "GET":
                        return "value: %s" % getattr(self.thing, attr)
                    elif request.method == "PUT":
                        value = request.data
                        if attrtype=="int":
                            value = int(value)
                        if attrtype=="float":
                            value = int(value)
                        if attrtype=="str":
                            value = str(value)
                        if attrtype=="bool":
                            value = True if value == "True" else False

                        setattr(self.thing, attr, value)
                        x = getattr(self.thing, attr)
                        return "set_attr: %s to %s, result %s.. " % (repr(attr), repr(value), repr(x))
                    return "I FAILED!"
                except Exception as e:
                    return "I *DIED* !" + repr(e)

            handle_attr.func_name = "handle_%s" % attr

            app.route("/"+attr, methods=["GET","PUT"])(handle_attr)

        for func in self.devinfo["funcs"]:
            funcspec = self.devinfo["funcs"][func]
            def handle_func(func=func,funcspec=funcspec):
                global request
                try:
                    if request.method == "GET":
                        return "get func: %s" % json.dumps(funcspec)
                    elif request.method == "PUT":
                        raise Exception("PUT NOT SUPPORTED FOR FUNCTIONS")
                    elif request.method == "POST":
                        value = request.data
                        if funcspec["spec"]["args"]!=[]:
                            pass
                        else:
                            args = []
                            #if attrtype=="int":
                                #value = int(value)
                            #if attrtype=="float":
                                #value = int(value)
                            #if attrtype=="str":
                                #value = str(value)
                            #if attrtype=="bool":
                                #value = True if value == "True" else False

                        # setattr(self.thing, attr, value)
                        # x = getattr(self.thing, attr)
                        result = getattr(self.thing, func)(*args)
                        return "callfunction: %s(%s) -> %s " % (str(func), str(value), repr(result))
                    return "FUNC FAILED!"
                except Exception as e:
                    return "FUNC *DIED* !" + repr(e)

            handle_func.func_name = "handle_%s" % func
            funcspec["href"] = "/"+func
            funcspec["methods"] = ["GET","POST"]

            app.route(funcspec["href"], methods=["GET","PUT","POST"])(handle_func)

        # Basic test of automated method / stem creation -- To be deleted
        for stem in self.devinfo.keys():
            def test(stem=stem):
                return stem
            test.func_name = stem
            app.route("/"+stem, methods=["GET"])(test)

        # Basic test of method / stem creation -- To be deleted
        def rootspec():
            return json.dumps(self.devinfo,indent=4)
        app.route("/", methods=["GET"])(rootspec)

        self.ready = True
        app.run(host='0.0.0.0')

default_host = "../../Arduino/libraries/IOToy/examples/TestHostTiny/build-stdio/TestHostStdio"

try:
    os.stat(default_host)
except OSError:
    print "=================================================================="
    print
    print "  For this to work, you need to build the example:"
    print default_host
    print
    print "eg:"
    print
    print "cd ./libraries/IOToy/examples/TestHostTiny/"
    print "make -f Makefile_mock"
    print
    print "=================================================================="
    raise

io = commandio(default_host)
proxy = DeviceProxy(device=io)
proxy.introspect_device()

dev_interface = DeviceWebInterface(proxy)
dev_interface.start()
dev_interface.wait_server_start()

# Wait for the web interface thread to exit...
while True:
    time.sleep(1)

# Shell tests:
"""
michael@linux:~$ for i in 1000 2000 3000 4000; do (echo -e "PUT /turn_time_ms HTTP/1.0\nContent-Length: 4\n"; echo -n "$i")|netcat 127.0.0.1 5000 ; echo; done
michael@linux:~$ for i in turn_time_ms test attrs funcs devicename; do echo -e "GET /$i HTTP/1.0\n\n" |netcat 127.0.0.1 5000 ; echo; done
michael@linux:~$ for i in 1000 2000 3000 4000; do (echo -e "PUT /drive_forward_time_ms HTTP/1.0\nContent-Length: 4\n"; echo -n "$i")|netcat 127.0.0.1 5000 ; echo; done
michael@linux:~$ echo -e "GET / HTTP/1.0\n\n"| netcat 127.0.0.1 5000; echo; for i in 1000; do (echo -e "GET /barecommand HTTP/1.0\n\n"; echo -n "1")|netcat 127.0.0.1 5000 ; echo; done ; for i in barecommand no_arg_result_int no_arg_result_bool no_arg_result_str no_arg_result_float no_arg_result_T; do (echo -e "POST /$i HTTP/1.0\nContent-Length: 0\n\n"; echo -n "")|netcat 127.0.0.1 5000 ; echo; done
"""
