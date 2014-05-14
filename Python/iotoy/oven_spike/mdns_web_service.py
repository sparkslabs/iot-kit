#!/usr/bin/python

import json
import select
import threading

from flask import jsonify, make_response, request
import pybonjour

# Make available to the user of this spike file.
from iotoy.value_types import IOTOY_INT, IOTOY_DIR, IOTOY_OBJ, IOTOY_EXCEPTION, IOTOY_METHOD
from iotoy.utils import http_debug
from iotoy.webinterface import WebInterface

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
