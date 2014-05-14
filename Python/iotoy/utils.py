#!/usr/bin/python

import pprint

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


def props(thing):
    """\
    This function allows us to inspect IOT proxy objects to
    find out what they can do...
    """
    thing_keys = thing.__dict__.keys()
    class_keys = thing.__class__.__dict__.keys()
    return [x for x in list(set(thing_keys + class_keys)) if x[0] != "_"]
