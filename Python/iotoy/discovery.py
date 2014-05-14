#!/usr/bin/python


import select
import socket
import pybonjour

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


