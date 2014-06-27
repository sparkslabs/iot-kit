#!/usr/bin/python

import sys
from iotoy.discovery import find_device

mod = sys.__class__
def greet(greeting="Hello World"):
   print greeting

class AutoLoad(mod):
    """This module is actually replaced by an Autoload class at startup.

    This allows us to ask this module to automatically find devices on the local network
    It can be used like this:
    
    from iotoy.local import sumobot
    
    sumobot.forward()
    
    etc
    """

    def __init__(self, mod_name):
        super(AutoLoad, self).__init__("home")
        self.wrapped_name = mod_name
        self.wrapped = sys.modules[mod_name]
    def __getattr__(self, name):
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            device = find_device(name)
            return device

if __name__ == "__main__":
    pass
else:               # Could use != above, but this is to be in your face about logic!
    import sys
    sys.modules[__name__] = AutoLoad(__name__)
