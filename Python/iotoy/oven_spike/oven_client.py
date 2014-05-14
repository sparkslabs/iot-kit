#!/usr/bin/python

import json
import requests

# Make available to the user of this spike file.
from iotoy.value_types import IOTOY_INT, IOTOY_DIR, IOTOY_OBJ, IOTOY_EXCEPTION, IOTOY_METHOD
from iotoy.utils import props
from iotoy.discovery import mdns_lookup


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
