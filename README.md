# IOT Kit - An IOT Tool Kit For Makers
### Make an Internet of Things (Of Yours)

IOT-Kit is a collection of tools for creating and working with devices that
can be controlled, connected to each other to form *an* Internet of Things
(of Yours).

The system focusses on the peer-to-peer networking usecase, though there
are wider plans. The aim is to get local networking and internetworking
first before moving that to the next stage.

**It is intended to be very maker friendly:**

* If you can make any simple arduino device you can use IOT-Kit
  to make it an IOT device.
* If you can python any python, you can use any IOT-Kit  ased device.

## Tutorial?

A basic overview tutorial is here:
* <http://www.sparkslabs.com/michael/blog/2018/02/12/hello-iot-kit,-introduction-by-example>

It explains how to build a simple network controllable arduino robot.

It assumes you know how to use 2 continuous rotation servos + simple arduino
to make a robot, guides you through programming a simple interaction layer,
through to slapping on the IOT interface using IOT-Kit.

OK, it's more of a guided walkthrough than a tutorial, and it misses out a
couple of interesting bits, but it gives you a start before you delve into
the project!

## Status : Stable

Since of 2014, the peer-to-peer level technologies have been stable.
Occasionally work is done on the higher level specs and use case ideas.

## Overview

IOT-Kit consists of:

* A collection of pieces allowing serial control (wired or BT) and
  introspection of an arduino device.

* A mapping of that to a python proxy

* A mapping of that python proxy to a RESTful JSON based service.

* Automatic advertisement of that service on a local mDNS interface -
  with the service name derived from the arduino API

* A python API for "importing" IOT devices. In particular treating
  devices like python packages.

* A python API for then mapping the RESTful interface back to python
  linguistic rules.

## Peer to Peer Network Control

The idea being that you can build your own little robots or sensors.
Once you've done that being able to do the minimum to allow it to be
controlled using high level python code over a local network connection
doing something like this:

    from iotoy.local import robot

    ON = 1
    robot.forward()
    robot.led = ON
    if robot.sensor >255:
       robot.forward()

    print robot.sensor.__doc__

Among the examples is a simple TestHost and a simple BotHost. BotHost controls
a simple robot.

## Enabling Peer to Peer Control

TestHost demonstrates the wider aspects of the API, so I'll describe this below.
This allows you to plug in a testhost device to a server host. Then on that
machine do this:

    michael@home:~/Development/iotoy/Python/examples$ ./webhost_for_arduino_device.py

## Introspecting a local REST IOT service

That the communicates with the device, finds out what it does and create the
RESTful web service. You can then do this:

    michael@home:~$ python
    Python 2.7.6 (default, Mar 22 2014, 22:59:56) 
    [GCC 4.8.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from iotoy.local import testhosttiny
    >>> testhosttiny
    <iotoy.discovery.testhosttiny object at 0x7f7add452350>
    >>> help(testhosttiny)
    { Screen shows help from the introspected device }
    >>> pprint.pprint(testhosttiny.devinfo)
    {u'attrs': {u'drive_forward_time_ms': {u'help': u'How long to move forward',
                                           u'href': u'/drive_forward_time_ms',
                                           u'type': u'int'},
                u'ratio': {u'help': u'Sample float attribute',
                           u'href': u'/ratio',
                           u'type': u'float'},
                u'some_flag': {u'help': u'Sample bool attribute',
                               u'href': u'/some_flag',
                               u'type': u'bool'},
                u'str_id': {u'help': u'Sample str attribute',
                            u'href': u'/str_id',
                            u'type': u'str'},
                u'turn_time_ms': {u'help': u'How long to turn',
                                  u'href': u'/turn_time_ms',
                                  u'type': u'int'}},
     u'devicename': u'testhosttiny',
     u'funcs': {u'barecommand': {u'help': u'test, basic command, no arg/result',
                                 u'href': u'/barecommand',
                                 u'type': 'iotoy.org/types/function',
                                 u'value': {u'name': u'barecommand',
                                            u'spec': {u'args': [],
                                                      u'result': []}}},
                u'no_arg_result_T': {u'help': u'test, one arg, generic type',
                                     u'href': u'/no_arg_result_T',
                                     u'type': 'iotoy.org/types/function',
                                     u'value': {u'name': u'no_arg_result_T',
                                                u'spec': {u'args': [],
                                                          u'result': [[u'result',
                                                                       u'T']]}}},
                u'no_arg_result_bool': {u'help': u'test, one arg, boolean',
                                        u'href': u'/no_arg_result_bool',
                                        u'type': 'iotoy.org/types/function',
                                        u'value': {u'name': u'no_arg_result_bool',
                                                   u'spec': {u'args': [],
                                                             u'result': [[u'result',
                                                                          u'bool']]}}},
                u'no_arg_result_float': {u'help': u'test, one arg, float',
                                         u'href': u'/no_arg_result_float',
                                         u'type': 'iotoy.org/types/function',
                                         u'value': {u'name': u'no_arg_result_float',
                                                    u'spec': {u'args': [],
                                                              u'result': [[u'result',
                                                                           u'float']]}}},
                u'no_arg_result_int': {u'help': u'test, one arg, integer',
                                       u'href': u'/no_arg_result_int',
                                       u'type': 'iotoy.org/types/function',
                                       u'value': {u'name': u'no_arg_result_int',
                                                  u'spec': {u'args': [],
                                                            u'result': [[u'result',
                                                                         u'int']]}}},
                u'no_arg_result_str': {u'help': u'test, one arg, string',
                                       u'href': u'/no_arg_result_str',
                                       u'type': 'iotoy.org/types/function',
                                       u'value': {u'name': u'no_arg_result_str',
                                                  u'spec': {u'args': [],
                                                            u'result': [[u'result',
                                                                         u'str']]}}},
                u'one_arg_T': {u'help': u'test, one arg, generic type',
                               u'href': u'/one_arg_T',
                               u'type': 'iotoy.org/types/function',
                               u'value': {u'name': u'one_arg_T',
                                          u'spec': {u'args': [[u'attr', u'T']],
                                                    u'result': []}}},
                u'one_arg_bool': {u'help': u'test, one arg, boolean',
                                  u'href': u'/one_arg_bool',
                                  u'type': 'iotoy.org/types/function',
                                  u'value': {u'name': u'one_arg_bool',
                                             u'spec': {u'args': [[u'myarg',
                                                                  u'bool']],
                                                       u'result': []}}},
                u'one_arg_float': {u'help': u'test, one arg, float',
                                   u'href': u'/one_arg_float',
                                   u'type': 'iotoy.org/types/function',
                                   u'value': {u'name': u'one_arg_float',
                                              u'spec': {u'args': [[u'myarg',
                                                                   u'float']],
                                                        u'result': []}}},
                u'one_arg_int': {u'help': u'test, one arg, integer',
                                 u'href': u'/one_arg_int',
                                 u'type': 'iotoy.org/types/function',
                                 u'value': {u'name': u'one_arg_int',
                                            u'spec': {u'args': [[u'myarg',
                                                                 u'int']],
                                                      u'result': []}}},
                u'one_arg_int_result_int': {u'help': u'test, one arg, one result, both ints',
                                            u'href': u'/one_arg_int_result_int',
                                            u'type': 'iotoy.org/types/function',
                                            u'value': {u'name': u'one_arg_int_result_int',
                                                       u'spec': {u'args': [[u'myarg',
                                                                            u'int']],
                                                                 u'result': [[u'result',
                                                                              u'int']]}}},
                u'one_arg_str': {u'help': u'test, one arg, string',
                                 u'href': u'/one_arg_str',
                                 u'type': 'iotoy.org/types/function',
                                 u'value': {u'name': u'one_arg_str',
                                            u'spec': {u'args': [[u'myarg',
                                                                 u'str']],
                                                      u'result': []}}}}}

This API is entirely derived from the device itself. Various parts of automation
and similar are coming.

### Linguistic mapping of REST ###

The last thing that this project seeks to do is to implement something
RPC/SOAP like. Instead, this project works on the following assumptions.

In python:

    >>> x = module.SomeThing()
    >>> x
    <module.SomeThing object at 0xa11c44c>

In this it should be clear that in python you don't actually ever represent
with the actual hardware or data - just representations, and interact with
them via names. In particular, <code>SomeThing()</code> creates a resource,
which has a given representation. We can give that representation a
name - <code>x</code>.

From then on, we can do things like:

    >>> x.name = "Frank"
    >>> x.name
    'Frank'

In this case, <code>x.\_\_setattr_\_("name", "Frank")</code> sets a given
name to map to a given representation of bytes. Similarly the second like
performs <code>x.\_\_getattr_\_("name")</code>.

From this view, you can have the following mappings:

* <code>x</code> maps can be viewed as mapping to a web server
* <code>.name</code> can map to a given resource - eg <code>/names</code>
* <code>x.\_\_setattr_\_("name", "Frank")</code> is akin to <code>PUT /name HTTP/1.0 "Frank"</code>
* <code>x.\_\_getattr_\_("name")</code> is akin to <code>GET /name HTTP/1.0</code>
* Perhaps less obviously, <code>module.SomeThing()</code> maps:
    * module to a web server
    * <code>SomeThing</code> to a resource - most obviously <code>/SomeThing</code>
    * <code>module.SomeThing()</code> maps to <code>POST /SomeThing HTTP/1.0 _empty body_</code>


### License ###

You may use this code under the Apache 2 License. You may additionally use
this code under the GPL version 2, but ask for any/all patches back to be
provided under the apache 2 license (for simplicity's sake)

Original implementation ©copyright 2013 BBC.

Initial release 2014 by BBC Research & Development

Updates: 2018

### Contact ###

Michael Sparks

Website: http://www.sparkslabs.com/michael/
email: sparks DOT m AT gmail
twitter: @_sparkslabs
