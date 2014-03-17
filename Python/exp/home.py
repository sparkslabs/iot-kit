#!/usr/bin/python


def greet(greeting="Hello World"):
   print greeting

class AutoLoad(object):
    """This module is actually replaced by an Autoload class at startup.

    The reason for this is allow a user to have a means of querying the local network
    in a slightly more interesting way than they might otherwise"""

    def __init__(self, mod_name):
        super(AutoLoad, self).__init__()
        self.wrapped_name = mod_name
        self.wrapped = sys.modules[mod_name]
    def __getattr__(self, name):
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            def f():
                greet(name + " " + self.wrapped_name)
            return f

if __name__ == "__main__":
    pass
else:               # Could use != above, but this is to be in your face about logic!
    import sys
    sys.modules[__name__] = AutoLoad(__name__)
