#!/usr/bin/python

import json
import logging
import os
import pprint
import Queue
import select
import socket
import sys
import threading
import time

import flask
from flask import Flask, jsonify, make_response, request
import pybonjour
import requests

try:
    assert int(flask.__version__.split(".")[1]) > 8
except AssertionError:
    print
    print
    print "*******************************************************"
    print
    print "  Need flask version at least 0.9, 0.10 recommended"
    print "This is so that we can return appropriate status codes!"
    print
    print "*******************************************************"
    print
    print
    raise

IOTOY_INT = {
  "_type": "oven._iotoy._tcp.local/.well-known/iotoy/int_type",
  "_equiv": "iotoy.org/types/int"
}

IOTOY_DIR = {
  "_type": "oven._iotoy._tcp.local/.well-known/iotoy/dir_type",
  "_equiv": "iotoy.org/types/dir"
}

IOTOY_OBJ = {
  "_type": "oven._iotoy._tcp.local/.well-known/iotoy/obj_type",
  "_equiv": "iotoy.org/types/obj"
}

IOTOY_EXCEPTION = {
  "_type": "oven._iotoy._tcp.local/.well-known/iotoy/exception_type",
  "_equiv": "iotoy.org/types/exception"
}

IOTOY_EXCEPTION = {
  "_type": "oven._iotoy._tcp.local/.well-known/iotoy/method_type",
  "_equiv": "iotoy.org/types/method"
}


class DummySerial(object):
    def __init__(self, queuewrite, queueread):
        self.queuewrite = queuewrite
        self.queueread = queueread

    def write(self, data):
        self.queuewrite.put_nowait(data)

    def read(self, timeout=0.5):
        try:
            result = self.queueread.get(timeout=timeout)
            return result
        except Queue.Empty:
            return ""


def mkserial():
    A, B = Queue.Queue(), Queue.Queue()
    producer = DummySerial(A, B)
    consumer = DummySerial(B, A)
    return (producer, consumer)


def http_debug(request):
    """Given a request context, dump headers and any HTTP payload"""
    url = "%(SERVER_NAME)s:%(SERVER_PORT)s%(PATH_INFO)s" % request.environ
    todump = [("Server", url),
                  ("Method", "%(REQUEST_METHOD)s" % request.environ)
             ] + request.headers.to_list()
    for headerkey, headervalue in request.headers.to_list():
        if headerkey == "Content-Length" and headervalue != "0":
            todump += [request.data]
            break
    else:
        todump += [""]

    pprint.pprint(todump)


class WebInterface(threading.Thread):
    """Base class to assist with providing web APIs for IOT objects"""
    daemon = True

    # Thing attribute is provided as a utility for things that don't
    # want/need to provide a custom __init__ function
    def __init__(self, thing):
        threading.Thread.__init__(self)
        self.thing = thing
        self.ready = False
        self.app = None

    def run(self):
        self.app = app = Flask(__name__)
        baremethods = []
        for name in self.__class__.__dict__.keys():
            if name[0] != "_" and name not in ("daemon", "run"):
                baremethods.append(name)

        for method in baremethods:
            webmethod = method[:3]
            stem = method[3:].replace("__", "/")
            app.route(stem, methods=[webmethod])(getattr(self, method))

        self.ready = True
        app.run(host='0.0.0.0')


def mdns_lookup(requestedname="oven", regtype="_iotoy._tcp", suffix=".local."):
    requestedfullname = requestedname + "." + regtype + suffix

    timeout = 1
    queried = []
    resolved = []
    results = []

    def LOOKUP__query_record_callback(sdRef, flags, interfaceIndex,
                                      errorCode, fullname, rrtype,
                                      rrclass, rdata, ttl):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print '  IP         =', socket.inet_ntoa(rdata)
            queried.append(socket.inet_ntoa(rdata))

    def LOOKUP__resolve_callback(sdRef, flags, interfaceIndex,
                                 errorCode, fullname, hosttarget,
                                 port, txtRecord):
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        print 'Resolved service:'
        print '  fullname   =', fullname
        print '  hosttarget =', hosttarget
        print '  port       =', port

        lookup = [fullname, hosttarget, port]
        #FIXME
        query_sdRef = pybonjour.DNSServiceQueryRecord(\
                                    interfaceIndex=interfaceIndex,
                                    fullname=hosttarget,
                                    rrtype=pybonjour.kDNSServiceType_A,
                                    callBack=LOOKUP__query_record_callback)

        try:
            while not queried:
                ready = select.select([query_sdRef], [], [], timeout)
                if query_sdRef not in ready[0]:
                    raise Exception("Query Fail")
                    break
                pybonjour.DNSServiceProcessResult(query_sdRef)
            else:
                IP = queried.pop()
                # Check for full name acts as a filter
                # If we didn't do this we'd have to do a time based
                # thing instead, which may be more appropriate
                if fullname == requestedfullname:
                    print fullname
                    print requestedfullname
                    lookup.append(IP)
                    results.append(lookup)
        finally:
            query_sdRef.close()

        resolved.append(True)

    def LOOKUP__browse_callback(sdRef, flags, interfaceIndex,
                                errorCode, serviceName,
                                regtype, replyDomain):
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            print 'Service removed'
            return

        print 'Service added; resolving'

        resolve_sdRef = pybonjour.DNSServiceResolve(0,
                                                    interfaceIndex,
                                                    serviceName,
                                                    regtype,
                                                    replyDomain,
                                                    LOOKUP__resolve_callback)

        try:
            while not resolved:
                ready = select.select([resolve_sdRef], [], [], timeout)
                if resolve_sdRef not in ready[0]:
                    raise Exception("Resolve Fail")
                    break
                pybonjour.DNSServiceProcessResult(resolve_sdRef)
            else:
                resolved.pop()
        finally:
            resolve_sdRef.close()

    browse_sdRef = pybonjour.DNSServiceBrowse(regtype=regtype,
                                              callBack=LOOKUP__browse_callback)

    try:
        try:
            while True:
                ready = select.select([browse_sdRef], [], [], timeout)
                if browse_sdRef in ready[0]:
                    pybonjour.DNSServiceProcessResult(browse_sdRef)
                else:
                    # FIXME
                    raise Exception("Main Fail - means not found,"
                                    "let alone resolvable or queryable")
                if len(results) > 0:
                    print results
                    break
        except KeyboardInterrupt:
            pass
    finally:
        browse_sdRef.close()

    if results:
        return results
    else:
        raise Exception("Fail!")

######################################################################
#
# Domain specific objects
#
######################################################################

######################################################################
#
# ARDUINO MOCK CODE - for testing the high level code without needing Hardware
#
######################################################################


class ActualOven(threading.Thread):
    # Well, obviously not a "real" oven, simulation of an oven
    """This simulates an oven that we're communicating with over
    a serial connection. In particular, it simulates what we're
    communicating to. If there was an arduino on the system, this
    would be the arduino part"""
    daemon = True

    def __init__(self, fake_serial):
        super(ActualOven, self).__init__()
        self.fake_serial = fake_serial
        self._temp = 20
        self._target = 20

    def simulate_tick(self):
            if self._temp < self._target:
                if (self._target - self._temp) > 30:
                    self._temp += 15
                else:
                    self._temp = int((self._temp + self._target) / 2.0 + 0.5)
            if self._temp > self._target:
                self._temp = int((self._temp + self._target) / 2.0)

    def run(self):
        start = last = time.time()
        while True:
            now = time.time()
            if now - last > 0.5:
                self.simulate_tick()
                last = now
            raw_command = self.fake_serial.read()

            if raw_command:
                command = raw_command.split()
                if command[0] == "HELP":
                    self.fake_serial.write("HELP NOT YET IMPLEMENTED\n")
                if command[0] == "GET":
                    if command[1] == "temp":
                        self.fake_serial.write(str(self._temp) + "\n")
                    elif command[1] == "target":
                        self.fake_serial.write(str(self._target) + "\n")
                    else:
                        self.fake_serial.write("UNKNOWN GET")

                if command[0] == "SET":
                    if command[1] == "target":
                        self._target = int(command[2])
                        self.fake_serial.write("200 target ")
                        self.fake_serial.write(str(self._target) + "\n")
                    else:
                        self.fake_serial.write("UNSUPPORTED SET")

            time.sleep(0.01)


######################################################################
#
# SYSTEM PROXY - FOR INTERFACING WITH THE REAL OBJECT - EITHER DIRECTLY
# OR VIA SERIAL COMMS
#
######################################################################

class Oven(object):
    """\
    This is the local proxy for the physical device, that the
    network proxy uses to control the device"""
    daemon = True

    def __init__(self, ser):
        # Ser is the serial port we're using to communiate with
        # the IOT-able object
        self.ser = ser

    def get_targettemperature(self):
        """\
        This is the temperature that the oven is currently set
        to. This is always a target, not reality This could be a
        read-write property really
        """
        self.ser.write("GET target\n")
        result = self.ser.read()
        result = result.strip()
        result = int(result)
        return result

    def set_targettemperature(self, value):
        self.ser.write("SET target " + repr(value) + "\n")
        raw_result = self.ser.read()
        raw_result = raw_result.strip()
        result = raw_result.split()

    def temperature(self):
        """\
        This is the temperature that the oven currently is.
        You can't change this, just the target temp.
        """
        self.ser.write("GET temp\n")
        result = self.ser.read()
        result = result.strip()
        result = int(result)

        return result

######################################################################
#
# CONCRETE WEB INTERFACE FOR THE OVEN SYSTEM PROXY - ADVERTISED VIA MDNS
#
######################################################################


class OvenInterface(WebInterface):
    """\
    Naming convention

    METHOD__resource_name

    METHOD is an HTTP Method
    resource name is any resource name
    Double underscores become / in URL routes
    Currently no support for named parameters in the URL. Maybe later.
    """

    def __init__(self, thing):
        super(OvenInterface, self).__init__(thing)

    def PUT__target_temperature(self):
        http_debug(request)

        data = json.loads(request.data)
        self.thing.set_targettemperature(data["value"])
        set_to = self.thing.get_targettemperature()
        if set_to == data["value"]:
            return jsonify({"_meta": IOTOY_INT,
                            "value": self.thing.get_targettemperature()
                           })
        else:
            # Gateway error of somekind, setting failed
            return jsonify({"_meta": IOTOY_INT,
                            "value": set_to
                           })

    def GET__target_temperature(self):
        return jsonify({"_meta": IOTOY_INT,
                        "value": self.thing.get_targettemperature()
                       })

    def PUT__temperature(self):
        return jsonify({"_meta": IOTOY_EXCEPTION}), 405

    def GET__temperature(self):
        return jsonify({"_meta": IOTOY_INT,
                        "value": self.thing.temperature()
                       })

    def GET__(self):
        http_debug(request)
        #
        # FIXME: Response should be:
        # { "_meta" : IOTOY_DIR,
        #   "value" : ["temperature", "target_temperature"] }
        #
#        response = make_response(json.dumps(["temperature",
#                                             "target_temperature"]))
        response = make_response(json.dumps({"_meta": IOTOY_DIR,
                                             "value": ["temperature",
                                                       "target_temperature"]
                                            }))
        response.headers["Content-Type"] = "application/json"
        return response


#######################################################################
#
# mDNS SERVICE FOR THE CONCRETE WEB INTERFACE OF THE OVEN EXAMPLE
#
#######################################################################
class OvenService(threading.Thread):
    daemon = True

    def __init__(self, name="oven", regtype="_iotoy._tcp", port=5000):
        threading.Thread.__init__(self)
        self.name = name
        self.regtype = regtype
        self.port = port
        if port != 5000:
            self.name += str(port - 5000)
        self.sdRef = None

    def callback(self, sdRef, flags, errorCode, name, regtype, domain):
        print sdRef, flags, errorCode, name, regtype, domain
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print 'Registered service:'
            print '  name    =', name
            print '  regtype =', regtype
            print '  domain  =', domain

    def run(self):
        self.sdRef = sdRef = pybonjour.DNSServiceRegister(
                                                name=self.name,
                                                regtype=self.regtype,
                                                port=self.port,
                                                callBack=self.callback)
        try:
            try:
                while True:
                    ready = select.select([sdRef], [], [])
                    if sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(self.sdRef)
            except KeyboardInterrupt:
                pass
        finally:
            sdRef.close()

#######################################################################
#
# Client side code proxy for the mDNS advertised Web API.
#
# Provides a programmer friendly API which maps Python object access
# attributes to appropriate RESTful calls
#
#######################################################################


class oven_proxy(object):
    """\
    This is a proxy object for the real IOT device, wrapping up how
    the user communicates with it over HTTP
    """

    def __init__(self, oven_name):

        services = mdns_lookup(requestedname=oven_name,
                               regtype="_iotoy._tcp",
                               suffix=".local.")
        fullname, hostname, port, ip = services[0]
        self.service = "http://%s:%d" % (ip, port)
        print self.service
        result = requests.get(self.service + "/")

        assert result.status_code == 200
        print result.headers.get("content-type", None)
        assert result.headers.get("content-type", None) == "application/json"
        print "__init__", json.loads(result.content)

    def _set_target(self, value):
        result = requests.put(self.service + "/target_temperature",
                              data=json.dumps({"_meta": IOTOY_INT,
                                               "value": value}),
                              headers={'content-type': 'application/json'})
        assert result.status_code == 200
        assert result.headers.get("content-type", None) == "application/json"

    def _get_target(self):
        response = requests.get(self.service + "/target_temperature")
        assert response.status_code == 200
        assert response.headers.get("content-type", None) == "application/json"
        result = json.loads(response.content)
        return result["value"]

    # This is a property here, but should really be implemented using
    # getattr things in some shape or form.
    target_temperature = property(_get_target, _set_target)

    @property
    def temperature(self):
        response = requests.get(self.service + "/temperature")
        assert response.status_code == 200
        assert response.headers.get("content-type", None) == "application/json"
        result = json.loads(response.content)
        #print "temperature", result
        return result["value"]


def props(thing):
    """\
    This function allows us to inspect IOT proxy objects to
    find out what they can do...
    """
    thing_keys = thing.__dict__.keys()
    class_keys = thing.__class__.__dict__.keys()
    return [x for x in list(set(thing_keys + class_keys)) if x[0] != "_"]


########################################################################
#
# Example Code/ Test Harness, consists of two halves:
#    * Set up the test IOT object services etc
#    * Client side code that monitors the oven and makes it change
#      temperatures at given times.
#
# Currently Missing:
#    * __call__ - mapping to post
#    * Object data model - based on jsonpickle & .well-known / meta
#      ideas & JSON HOME proposed standard
#    * Non-local external proxy via httptunnel or similar.
#      (easy to bolt on, but needs integrating)
#    * Websockets for data subscribe / data publish
#      - To be represented as channels (active queues) with callbacks
#
#######################################################################

if __name__ == "__main__":
    pass
