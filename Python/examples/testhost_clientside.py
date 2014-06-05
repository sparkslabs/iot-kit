#!/usr/bin/python

import pprint

from iotoy.discovery import find_device

testhosttiny = find_device(devicename="testhosttiny")

pprint.pprint(testhosttiny.devinfo)
print
print testhosttiny.devinfo["attrs"].keys()
print
print "testhosttiny.ratio =", repr(testhosttiny.ratio)
print "testhosttiny.turn_time_ms =", repr(testhosttiny.turn_time_ms)
print "testhosttiny.drive_forward_time_ms =", repr(testhosttiny.drive_forward_time_ms)
print "testhosttiny.some_flag =", repr(testhosttiny.some_flag)
print "testhosttiny.str_id =", repr(testhosttiny.str_id)

testhosttiny.ratio = 1.23
print
print "testhosttiny.ratio =", repr(testhosttiny.ratio)

print dir(testhosttiny.__class__.__name__)
print testhosttiny.__class__.__name__

print testhosttiny.devinfo["funcs"].keys()
print "testhosttiny.barecommand()", repr(testhosttiny.barecommand())
print "testhosttiny.no_arg_result_int()", repr(testhosttiny.no_arg_result_int())
print "testhosttiny.no_arg_result_bool()", repr(testhosttiny.no_arg_result_bool())
print "testhosttiny.no_arg_result_T()", repr(testhosttiny.no_arg_result_T())
print "testhosttiny.no_arg_result_bool()", repr(testhosttiny.no_arg_result_bool())
print "testhosttiny.no_arg_result_str()", repr(testhosttiny.no_arg_result_str())
print "testhosttiny.no_arg_result_float()", repr(testhosttiny.no_arg_result_float())

print 'testhosttiny.one_arg_T("hello")', repr(testhosttiny.one_arg_T("hello"))
print "testhosttiny.one_arg_int_result_int(1)", repr(testhosttiny.one_arg_int_result_int(1))
print "testhosttiny.one_arg_bool(True)", repr(testhosttiny.one_arg_bool(True))
print "testhosttiny.one_arg_int(100)", repr(testhosttiny.one_arg_int(100))
print 'testhosttiny.one_arg_str("wibble")', repr(testhosttiny.one_arg_str("wibble"))
print "testhosttiny.one_arg_float(1.78)", repr(testhosttiny.one_arg_float(1.78))

#help(testhosttiny)

print dir(testhosttiny)

