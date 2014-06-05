#!/usr/bin/python


import select
import socket
import pybonjour
import threading
import time
import json
import requests

class DeviceError(Exception):
    pass

def mdns_lookup(requestedname="testhosttiny", regtype="_iotoy._tcp", suffix=".local."):
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

####################################
#
# Advertise webservices over mDNS
#
####################################
class IOTWebService(threading.Thread):
    daemon = True

    def __init__(self, name="testhosttiny", regtype="_iotoy._tcp", port=5000):
        threading.Thread.__init__(self)
        self.name = name
        self.regtype = regtype
        self.port = port
        if port != 5000:
            self.name += str(port - 5000)
        self.sdRef = None
        self.ready = False

    def callback(self, sdRef, flags, errorCode, name, regtype, domain):
        print sdRef, flags, errorCode, name, regtype, domain
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print 'Registered service:'
            print '  name    =', name
            print '  regtype =', regtype
            print '  domain  =', domain
        self.ready = True

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

    def wait_advertised(self):
        while not self.ready:
            time.sleep(0.01)


def find_device(devicename):
    services = mdns_lookup(requestedname=devicename,
                           regtype="_iotoy._tcp",
                           suffix=".local.")
    fullname, hostname, port, ip = services[0]
    service = "http://%s:%d" % (ip, port)
    result = requests.get(service + "/")
    assert result.status_code == 200
    assert result.headers.get("content-type", None) == "application/json"
    tld = json.loads(result.content)

    if not (tld["type"] == "iotoy.org/type/dir" and "devinfo" in tld["value"] ):
        raise DeviceError("Device does not support the iotoy protocol at this time")

    result = requests.get(service + "/devinfo")
    assert result.status_code == 200
    assert result.headers.get("content-type", None) == "application/json"
    devinfo = json.loads(result.content)
    assert devinfo["type"] == "iotoy.org/type/json"
    rawdevinfo = devinfo
    devinfo = rawdevinfo["value"]
    #print rawdevinfo["help"]

    config = {
        "service" : service,
        "fullname" : fullname,
        "hostname" : hostname,
        "ip" : ip,
        "port" : port,
        "devicename" : devicename,
        "tld" :tld,
        "rawdevinfo": rawdevinfo,
        "devinfo": devinfo,
        "href" : rawdevinfo["href"]
    }

    class ClientsideProxy(object):
        __doc__ = """\
        %s

        This a proxy object for a %s. It does this: %s
        """ % (devicename,devicename, rawdevinfo["help"])

        def _configure(self, config):
            self.service = config["service"]
            self.fullname = config["fullname"]
            self.hostname = config["hostname"]
            self.ip = config["ip"]
            self.port = config["port"]
            self.devicename = config["devicename"]
            self.tld = config["tld"]
            self.rawdevinfo = config["rawdevinfo"]
            self.devinfo = config["devinfo"]
            self.__href__ = config["href"]
            self._make_attributes()
            self._make_functions()

        def __init__(self, device_name):
            self.device_name = device_name

        def _make_attributes(self):
            for attr in self.devinfo["attrs"]:
                def get_attr(self,attr=attr):
                    result = requests.get(self.service + "/" + attr)
                    assert result.status_code == 200
                    assert result.headers.get("content-type", None) == "application/json"
                    raw_json = json.loads(result.content)
                    return raw_json["value"]

                def put_attr(self,value, attr=attr):
                    response = requests.put(self.service + "/" + attr, data=str(value))
                    assert response.status_code == 200
                    assert response.headers.get("content-type", None) == "application/json"
                    raw_json = json.loads(response.content)
                    return raw_json["value"]

                setattr(self.__class__,attr,property(get_attr,put_attr, None,self.devinfo["attrs"][attr]["help"]))
                #print "make getter for attr", attr
                #print "make setter for attr", attr
                #print "make property for attr", attr
                #print "set docstring for attr", attr
            setattr(self.__class__,"a_doc",property(None,None, None,self.rawdevinfo["help"]))

        def _make_functions(self):
            for func in self.devinfo["funcs"]:
                funcspec = self.devinfo["funcs"][func]
                #print funcspec
                funcspec["type"] = "iotoy.org/types/function"
                funcspec["href"] = "/"+funcspec["value"]["name"]
                funcspec["help"] = funcspec["help"]
                if len(funcspec["value"]["spec"]["args"]) == 0:
                    def handle_func(self,_iot=(funcspec,func)):
                        funcspec,func_name=_iot
                        response = requests.post(self.service + "/" + func_name, data="")
                        assert response.status_code == 200
                        assert response.headers.get("content-type", None) == "application/json"
                        raw_json = json.loads(response.content)
                        return raw_json["value"]

                elif len(funcspec["value"]["spec"]["args"]) == 1:
                    def handle_func(self, arg,_iot=(funcspec,func)):
                        funcspec,func_name=_iot
                        response = requests.post(self.service + "/" + func_name, data=str(arg))
                        assert response.status_code == 200
                        assert response.headers.get("content-type", None) == "application/json"
                        raw_json = json.loads(response.content)
                        return raw_json["value"]
                else:
                    raise DeviceError("Device handles functions with >1 arg, we don't")

                handle_func.func_name = str(func)
                handle_func.__doc__ = funcspec["help"]
                setattr(self.__class__,func,handle_func)

    ClientsideProxy.__name__ = devicename
    client = ClientsideProxy(devicename)
    client._configure(config)
    return client
