#!/usr/bin/python

import threading
import flask

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


