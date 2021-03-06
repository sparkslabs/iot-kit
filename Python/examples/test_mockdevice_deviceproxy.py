#!/usr/bin/python

import os

from iotoy.deviceproxy import commandio, DeviceProxy

default_host = "../../Arduino/libraries/IOToy/examples/TestHostTiny/build-stdio/TestHostStdio"
default_host = "../../Arduino/libraries/IOToy/examples/BotHostTiny/build-stdio/BotHostStdio"

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
    print "cd ./libraries/IOToy/examples/BotHostTiny/"
    print "make -f Makefile_mock"
    print
    print "cd ./libraries/IOToy/examples/TestHostTiny/"
    print "make -f Makefile_mock"
    print
    print "=================================================================="
    raise

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

if default_host.endswith("TestHostStdio"):

    print p.barecommand
    p.barecommand()

    p.one_arg_int
    p.one_arg_int(1)
    try:
        p.one_arg_int(1.1)
    except ValueError as e:
        if e.message != "Should be int, recieved float":
           raise
        print "Successfully caught bad argument:", e

    try:
        p.one_arg_int("hello")
    except ValueError as e:
        if e.message != "Should be int, recieved str":
           raise
        print "Successfully caught bad argument:", e

    try:
        p.one_arg_int(True)
    except ValueError as e:
        if e.message != "Should be int, recieved bool":
           raise
        print "Successfully caught bad argument:", e

    p.one_arg_str("hello")
    try:
        p.one_arg_str(1)
    except ValueError as e:
        if e.message != "Should be str, recieved int":
           raise
        print "Successfully caught bad argument:", e

    try:
        print p.one_arg_str(1.1)
    except ValueError as e:
        if e.message != "Should be str, recieved float":
           raise
        print "Successfully caught bad argument:", e

    try:
        p.one_arg_str(True)
    except ValueError as e:
        if e.message != "Should be str, recieved bool":
           raise
        print "Successfully caught bad argument:", e

    p.one_arg_float(1.1)
    try:
        p.one_arg_float(1)
    except ValueError as e:
        if e.message != "Should be float, recieved int":
           raise
        print "Successfully caught bad argument:", e

    try:
        p.one_arg_float("hello")
    except ValueError as e:
        if e.message != "Should be float, recieved str":
           raise
        print "Successfully caught bad argument:", e

    try:
        p.one_arg_float(True)
    except ValueError as e:
        if e.message != "Should be float, recieved bool":
           raise
        print "Successfully caught bad argument:", e

    print p.no_arg_result_int()
    print p.no_arg_result_bool()
    print p.no_arg_result_str()
    print p.no_arg_result_float()
    print p.no_arg_result_T()

if default_host.endswith("BotHostStdio"):
    print p.forward()
    print p.backward()
    print p.left()
    print p.right()
    print p.on()
    print p.off()


