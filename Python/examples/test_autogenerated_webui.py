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
            attrhelp = self.devinfo["attrs"][attr]["help"]
            def handle_attr(attr=attr,attrtype=attrtype,attrhelp=attrhelp):
                global request
                try:
                    if request.method == "GET":
                        return flask.jsonify({ "value": getattr(self.thing, attr),
                                               "type": "iotoy.org/types/%s" % attrtype,
                                               "help": attrhelp,
                                               "href":"/"+attr })
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
                        return flask.jsonify({ "value": x,
                                               "type": "iotoy.org/types/%s" % attrtype,
                                               "help": attrhelp,
                                               "href":"/"+attr })

#                        return "set_attr: %s to %s, result %s.. " % (repr(attr), repr(value), repr(x))
                    return "I FAILED!"
                except Exception as e:
                    return "I *DIED* !" + repr(e)

            handle_attr.func_name = "handle_%s" % attr

            app.route("/"+attr, methods=["GET","PUT"])(handle_attr)

        for func in self.devinfo["funcs"]:
            funcspec = self.devinfo["funcs"][func]
            funcspec["type"] = "iotoy.org/types/function"
            funcspec["href"] = "/"+funcspec["value"]["name"]
            funcspec["help"] = "/"+funcspec["value"]["help"]
            del funcspec["value"]["help"]
            def handle_func(func=func,funcspec=funcspec):
                global request
                try:
                    if request.method == "GET":
                        return flask.jsonify(funcspec)
                    elif request.method == "PUT":
                        raise Exception("PUT NOT SUPPORTED FOR FUNCTIONS")
                    elif request.method == "POST":
                        value = request.data
                        if funcspec["value"]["spec"]["args"]!=[]:
                            value = request.data
                            func_args = funcspec["value"]["spec"]["args"]
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

                        result = getattr(self.thing, func)(*args)
                        result_spec = funcspec["value"]["spec"]["result"]
                        if len(result_spec) == 0:
                            return_value = { "type": "iotoy.org/types/null",
                                             "value" : None
                                           }
                        else:
                            resultname, resulttype = result_spec[0]
                            return_value = { "type" : resulttype,
                                             "name" : resultname,
                                             "value" : result
                                           }
                        return flask.jsonify(return_value)
#                        return "callfunction: %s(%s) -> %s " % (str(func), str(value), repr(result))

                    return "FUNC FAILED!"
                except Exception as e:
                    print "FAILURE!"
                    traceback.print_exc()
                    return "FUNC *DIED* !" + repr(e)

            handle_func.func_name = "handle_%s" % func
            funcspec["href"] = "/"+func

            app.route(funcspec["href"], methods=["GET","PUT","POST"])(handle_func)

        # Basic test of automated method / stem creation -- To be deleted
        for stem in self.devinfo.keys():
            def test(stem=stem):
                return stem
            test.func_name = stem
            app.route("/"+stem, methods=["GET"])(test)

        def devinfo_spec():
            return flask.jsonify({"type":"iotoy.org/type/json",
                                  "href" : "/devinfo",
                                  "help" : "Device description",
                                  "value": self.devinfo})
        app.route("/devinfo", methods=["GET"])(devinfo_spec)

        # Basic test of method / stem creation -- To be deleted
        def rootspec():
            tld = []
            tld += list(self.devinfo["funcs"].keys())
            tld += list(self.devinfo["attrs"].keys())
            tld.append("devinfo")
            result = { "type": "iotoy.org/type/dir",
                       "href" : "/",
                       "help" : self.devinfo["devicename"],
                       "value": tld
                      }
            pprint.pprint(result)
            return flask.jsonify(result)
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

    assert response.status_code == 200
    assert response.headers.get("content-type", None) == "application/json"
    result = json.loads(response.content)
    assert result["value"] == value
    assert result["type"] == "iotoy.org/types/int"


for value in 1000,2000,3000,4000,5000:
    response = requests.put("http://127.0.0.1:5000/drive_forward_time_ms", data=str(value))

    assert response.status_code == 200
    assert response.headers.get("content-type", None) == "application/json"
    result = json.loads(response.content)
    assert result["value"] == value
    assert result["type"] == "iotoy.org/types/int"

response = requests.get("http://127.0.0.1:5000/turn_time_ms")
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == 4000
assert result["type"] == "iotoy.org/types/int"

response = requests.get("http://127.0.0.1:5000/drive_forward_time_ms")
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == 5000
assert result["type"] == "iotoy.org/types/int"

response = requests.get("http://127.0.0.1:5000/ratio")        # {'type': 'float'}
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == 0.0
assert result["type"] == "iotoy.org/types/float"

response = requests.put("http://127.0.0.1:5000/ratio", data=str(3.1459))
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == 3.1459
assert result["type"] == "iotoy.org/types/float"

response = requests.get("http://127.0.0.1:5000/some_flag")    # {'type': 'bool'}
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == True
assert result["type"] == "iotoy.org/types/bool"

response = requests.put("http://127.0.0.1:5000/some_flag", data=str(True))
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == True
assert result["type"] == "iotoy.org/types/bool"

response = requests.put("http://127.0.0.1:5000/some_flag", data=str(False))
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == False
assert result["type"] == "iotoy.org/types/bool"


response = requests.get("http://127.0.0.1:5000/str_id")       # {'type': 'str'}
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == "default"
assert result["type"] == "iotoy.org/types/str"

response = requests.put("http://127.0.0.1:5000/str_id", data="random string")

assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == 'random string'
assert result["type"] == "iotoy.org/types/str"


# This behaviour will change (!)
for i in "attrs","funcs","devicename":
    response = requests.get("http://127.0.0.1:5000/%s" % i)
    response.content == i


# --------------------------------------------------
#
# Get the descriptions of all top level resources
#
# --------------------------------------------------
response = requests.get("http://127.0.0.1:5000/")
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["type"] == "iotoy.org/type/dir"
assert result["href"] == "/"
assert type(result["value"] == list)
top_level_resources = result["value"]
for resource in top_level_resources:
    response = requests.get("http://127.0.0.1:5000/"+resource)
    assert response.status_code == 200
    assert response.headers.get("content-type", None) == "application/json"
    result = json.loads(response.content)
    print "RESOURCE:", resource
    pprint.pprint(result)
    print

device_description_raw = requests.get("http://127.0.0.1:5000/devinfo")
print repr(device_description_raw.content)
print device_description_raw.headers
print device_description_raw.headers.get("content-type", None)
assert device_description_raw.headers.get("content-type", None) == "application/json"
device_description = json.loads(device_description_raw.content)
device_description = device_description["value"]
print device_description.keys()
print device_description["funcs"].keys()


# ----------------------------------------------------------------------
#
# Get the descriptions of all functions - from the device description
#
# ----------------------------------------------------------------------

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
    if func_description["value"]["spec"]["args"] == []:
        no_args.append(func_description)
    else:
        funcs_with_args.append(func_description)

    if func_description["value"]["spec"]["result"] != []:
        funcs_with_result.append(func_description)


# --------------------------------------------------
#
# Call functions which take no arguments
#
# --------------------------------------------------
print no_args
for func in no_args:
    func_name = func["value"]["name"]
    response = requests.post("http://127.0.0.1:5000/%s" % func_name, data="")
    print "FUNC CALL", func_name, (20-len(func_name))*" ", "::",
    print repr(response.content)
    print

# --------------------------------------------------
#
# Call all functions which take a single argument
#
# --------------------------------------------------
#print funcs_with_args
default_args = { # Values to pass in as default values
    "bool" : True,
    "int" : 73,
    "T": "3+4j",
    "str": "FTW",
    "float" : 3.14
}
for func in funcs_with_args:
    func_name = func["value"]["name"]
    func_args = func["value"]["spec"]["args"]
    print func_name, repr(func_args)
    assert len(func_args) == 1 # For the moment, only handle one argument per function
    arg_name, arg_type = func_arg = func_args[0]
    arg_value_to_send = default_args[arg_type]
    response = requests.post("http://127.0.0.1:5000/%s" % func_name, data=str(arg_value_to_send))
    print "FUNC CALL", func_name, (20-len(func_name))*" ", "::",
    print repr(response.content)
    print


# --------------------------------------------------
#
# Call all functions which produce a result
#
# --------------------------------------------------
print funcs_with_result
for func in funcs_with_result:
    func_name = func["value"]["name"]
    print func_name, func["value"]["spec"]["result"]
    if func["value"]["spec"]["args"]==[]:
        callarg = ""
    else:
        func_args = func["value"]["spec"]["args"]
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

"""
for i in barecommand one_arg_T no_arg_result_int no_arg_result_bool no_arg_result_T one_arg_int_result_int no_arg_result_str one_arg_int one_arg_bool no_arg_result_float one_arg_str one_arg_float str_id turn_time_ms drive_forward_time_ms some_flag ratio devinfo ; do  echo -e "GET /$i HTTP/1.0\n\n" |netcat 127.0.0.1 5000; echo; echo; done|less
"""