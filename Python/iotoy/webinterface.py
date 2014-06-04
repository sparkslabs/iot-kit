#!/usr/bin/python

import threading
import flask
from flask import request

import os
import time
import traceback

def webserver_started(port=5000):
    # This is really hacky, but there's no real workaround for this
    output = os.popen('netstat -nat').readlines()
    lines = [x.split()[3] for x in output if (x.startswith("tcp ") and ("LISTEN" in x) and (":5000" in x))]
    started = (len(lines) > 0 and lines[0].endswith(":5000"))
    return started

class DeviceWebInterface(threading.Thread):
    """Base class to assist with providing web APIs for IOT objects"""
    daemon = True

    # Thing attribute is provided as a utility for things that don't
    # want/need to provide a custom __init__ function
    def __init__(self, thing):
        threading.Thread.__init__(self)
        self.thing = thing
        self.ready = False
        self.app = None

    def wait_server_start(self, port=5000):
        while not webserver_started(port): # Avoid an annoying race hazard
            time.sleep(0.001)

    def run(self):
        self.devinfo = self.thing.devinfo()
        print self.thing
        self.app = app = flask.Flask(__name__)

        # Add the routes and methods for handling attributes
        # including appropriate data conversions/enforcement
        for attr in self.devinfo["attrs"]:
            attrtype = self.devinfo["attrs"][attr]["type"]
            self.devinfo["attrs"][attr]["href"] = "/"+attr
            attrhelp = self.devinfo["attrs"][attr]["help"]
            def handle_attr(attr=attr,attrtype=attrtype,attrhelp=attrhelp):
                global request
                try:
                    if request.method == "GET":
                        return flask.jsonify({ "value": getattr(self.thing, attr),
                                               "type": "iotoy.org/types/%s" % attrtype,
                                               "help": attrhelp,
                                               "href":"/"+attr })
                    elif request.method == "PUT":
                        value = request.data
                        if attrtype=="int":
                            value = int(value)
                        if attrtype=="float":
                            value = float(value)
                        if attrtype=="str":
                            value = str(value)
                        if attrtype=="bool":
                            value = True if value == "True" else False

                        setattr(self.thing, attr, value)

                        x = getattr(self.thing, attr)
                        return flask.jsonify({ "value": x,
                                               "type": "iotoy.org/types/%s" % attrtype,
                                               "help": attrhelp,
                                               "href":"/"+attr })

                    return "I FAILED!"
                except Exception as e:
                    return "I *DIED* !" + repr(e)

            handle_attr.func_name = "handle_%s" % attr

            app.route("/"+attr, methods=["GET","PUT"])(handle_attr)

        for func in self.devinfo["funcs"]:
            funcspec = self.devinfo["funcs"][func]
            funcspec["type"] = "iotoy.org/types/function"
            funcspec["href"] = "/"+funcspec["value"]["name"]
            funcspec["help"] = funcspec["value"]["help"]
            del funcspec["value"]["help"]
            def handle_func(func=func,funcspec=funcspec):
                global request
                try:
                    if request.method == "GET":
                        return flask.jsonify(funcspec)
                    elif request.method == "PUT":
                        raise Exception("PUT NOT SUPPORTED FOR FUNCTIONS")
                    elif request.method == "POST":
                        value = request.data
                        if funcspec["value"]["spec"]["args"]!=[]:
                            value = request.data
                            func_args = funcspec["value"]["spec"]["args"]
                            assert len(func_args) == 1 # For the moment, only handle one argument per function
                            arg_name, arg_type = func_arg = func_args[0]
                            if arg_type=="int":
                                value = int(value)
                            elif arg_type=="float":
                                value = float(value)
                            elif arg_type=="str":
                                value = str(value)
                            elif arg_type=="bool":
                                value = True if value == "True" else False
                            elif arg_type=="T":
                                value = str(value)
                            else:
                                raise NotImplementedError("Function calling with *that* argument type not yet handled :-)")
                            args = [value]
                        else:
                            args = []

                        result = getattr(self.thing, func)(*args)
                        result_spec = funcspec["value"]["spec"]["result"]
                        if len(result_spec) == 0:
                            return_value = { "type": "iotoy.org/types/null",
                                             "value" : None
                                           }
                        else:
                            resultname, resulttype = result_spec[0]
                            return_value = { "type" : resulttype,
                                             "name" : resultname,
                                             "value" : result
                                           }
                        return flask.jsonify(return_value)

                    return "FUNC FAILED!"
                except Exception as e:
                    print "FAILURE!"
                    traceback.print_exc()
                    return "FUNC *DIED* !" + repr(e)

            handle_func.func_name = "handle_%s" % func
            funcspec["href"] = "/"+func

            app.route(funcspec["href"], methods=["GET","PUT","POST"])(handle_func)

        def devinfo_spec():
            return flask.jsonify({"type":"iotoy.org/type/json",
                                  "href" : "/devinfo",
                                  "help" : "Device description",
                                  "value": self.devinfo})
        app.route("/devinfo", methods=["GET"])(devinfo_spec)

        def rootspec():
            tld = []
            tld += list(self.devinfo["funcs"].keys())
            tld += list(self.devinfo["attrs"].keys())
            tld.append("devinfo")
            result = { "type": "iotoy.org/type/dir",
                       "href" : "/",
                       "help" : self.devinfo["devicename"],
                       "value": tld
                      }
            return flask.jsonify(result)
        app.route("/", methods=["GET"])(rootspec)

        self.ready = True
        app.run(host='0.0.0.0')


class WebInterface(threading.Thread): # DEPRECATED
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
        self.app = app = flask.Flask(__name__)
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
