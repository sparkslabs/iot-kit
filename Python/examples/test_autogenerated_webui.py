#!/usr/bin/python

import os
import pprint
import json
import time

from iotoy.deviceproxy import commandio, DeviceProxy
from iotoy.webinterface import webserver_started, DeviceWebInterface

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

response = requests.put("http://127.0.0.1:5000/ratio", data=str(3.145))
assert response.status_code == 200
assert response.headers.get("content-type", None) == "application/json"
result = json.loads(response.content)
assert result["value"] == 3.145
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