#!/usr/bin/python

import os
import pprint
import json
import time
import traceback
import sys

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
                            value = float(value)
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
                        funcspec["type"] = "iotoy.function"
                        return flask.jsonify(funcspec)
#                        return "get func: %s" % json.dumps(funcspec)
                    elif request.method == "PUT":
                        raise Exception("PUT NOT SUPPORTED FOR FUNCTIONS")
                    elif request.method == "POST":
                        value = request.data
                        if funcspec["spec"]["args"]!=[]:
                            value = request.data
                            func_args = funcspec["spec"]["args"]
                            assert len(func_args) == 1 # For the moment, only handle one argument per function
                            arg_name, arg_type = func_arg = func_args[0]
                            if arg_type=="int":
                                value = int(value)
                            elif arg_type=="float":
                                value = float(value)
                            elif arg_type=="str":
                                value = str(value)
                            elif arg_type=="bool":
                                value = True if value == "True" else False
                            elif arg_type=="T":
                                value = str(value)
                            else:
                                raise NotImplementedError("Function calling with *that* argument type not yet handled :-)")
                            args = [value]
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
                    print "FAILURE!"
                    traceback.print_exc()
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
            return flask.jsonify(self.devinfo)
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

# ==================================================================================
#
# CLIENT SIDE TESTS
#
# ==================================================================================

import requests
print "Running self diagnostic"
for value in 1000,2000,3000,4000:
    response = requests.put("http://127.0.0.1:5000/turn_time_ms", data=str(value))
    assert response.content == ( "set_attr: 'turn_time_ms' to %d, result %d.. " % (value, value))
    assert response.status_code == 200

for value in 1000,2000,3000,4000,5000:
    response = requests.put("http://127.0.0.1:5000/drive_forward_time_ms", data=str(value))
    assert response.content == ( "set_attr: 'drive_forward_time_ms' to %d, result %d.. " % (value, value))
    assert response.status_code == 200

response = requests.get("http://127.0.0.1:5000/turn_time_ms")
assert response.content == "value: 4000"

response = requests.get("http://127.0.0.1:5000/drive_forward_time_ms")
assert response.content == "value: 5000"

response = requests.get("http://127.0.0.1:5000/ratio")        # {'type': 'float'}
assert response.status_code == 200
assert response.content == "value: 0.0"

response = requests.put("http://127.0.0.1:5000/ratio", data=str(3.1459))
assert response.status_code == 200
assert response.content == "set_attr: 'ratio' to 3.1459, result 3.1459.. "


response = requests.get("http://127.0.0.1:5000/some_flag")    # {'type': 'bool'}
assert response.status_code == 200
assert response.content == "value: True"

response = requests.put("http://127.0.0.1:5000/some_flag", data=str(True))
assert response.status_code == 200
assert response.content == "set_attr: 'some_flag' to True, result True.. "

response = requests.put("http://127.0.0.1:5000/some_flag", data=str(False))
assert response.status_code == 200
assert response.content == "set_attr: 'some_flag' to False, result False.. "


response = requests.get("http://127.0.0.1:5000/str_id")       # {'type': 'str'}
assert response.status_code == 200
assert response.content == "value: default"

response = requests.put("http://127.0.0.1:5000/str_id", data="random string")
assert response.status_code == 200
assert response.content == "set_attr: 'str_id' to 'random string', result 'random string'.. "

# This behaviour will change (!)
for i in "attrs","funcs","devicename":
    response = requests.get("http://127.0.0.1:5000/%s" % i)
    response.content == i

device_description_raw = requests.get("http://127.0.0.1:5000/")
print repr(device_description_raw.content)
print device_description_raw.headers
print device_description_raw.headers.get("content-type", None)
assert device_description_raw.headers.get("content-type", None) == "application/json"
device_description = json.loads(device_description_raw.content)
print device_description.keys()
print device_description["funcs"].keys()

func_names = device_description["funcs"].keys()
no_args = []
funcs_with_args = []
funcs_with_result = []
for func_name in func_names:
    response = requests.get("http://127.0.0.1:5000/%s" % func_name)
    assert response.headers.get("content-type", None) == "application/json"
    func_description = json.loads(response.content)
    print
    print "FUNCTION: ", func_name
    pprint.pprint(func_description)
    if func_description["spec"]["args"] == []:
        no_args.append(func_description)
    else:
        funcs_with_args.append(func_description)

    if func_description["spec"]["result"] != []:
        funcs_with_result.append(func_description)


print no_args
for func in no_args:
    func_name = func["name"]
    response = requests.post("http://127.0.0.1:5000/%s" % func_name, data="")
    print "FUNC CALL", func_name, (20-len(func_name))*" ", "::",
    print repr(response.content)
    print

#print funcs_with_args
default_args = { # Values to pass in as default values
    "bool" : True,
    "int" : 73,
    "T": "3+4j",
    "str": "FTW",
    "float" : 3.14
}
for func in funcs_with_args:
    func_name = func["name"]
    func_args = func["spec"]["args"]
    print func_name, repr(func_args)
    assert len(func_args) == 1 # For the moment, only handle one argument per function
    arg_name, arg_type = func_arg = func_args[0]
    arg_value_to_send = default_args[arg_type]
    response = requests.post("http://127.0.0.1:5000/%s" % func_name, data=str(arg_value_to_send))
    print "FUNC CALL", func_name, (20-len(func_name))*" ", "::",
    print repr(response.content)
    print

print funcs_with_result
for func in funcs_with_result:
    func_name = func["name"]
    print func_name, func["spec"]["result"]
    if func["spec"]["args"]==[]:
        callarg = ""
    else:
        func_args = func["spec"]["args"]
        arg_name, arg_type = func_arg = func_args[0]
        callarg = str(default_args[arg_type])

    response = requests.post("http://127.0.0.1:5000/%s" % func_name, data=callarg)
    print "FUNC CALL", func_name, (20-len(func_name))*" ", "::",
    print repr(response.content)
    print

print "Self diagnostic success"

# Wait for the web interface thread to exit
while True:
    time.sleep(1)
