#!/usr/bin/python

import os
import logging
import time

from iotoy.oven_spike import *
from iotoy.dummyserial import mkserial

#############################################################################################
#
# SET UP THE THING AND IT'S NETWORK ASPECTS
#
#############################################################################################

# Disable basic web logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# For testing at work, disable local proxy
if os.environ.get("http_proxy", False):
    del os.environ["http_proxy"]

# Create ourselves a fake serial object and a fake IOT object for testing purposes.
ser = mkserial()

# Create a software simulation of a physical thing. In a real world implementation, this would be an actual thing.
# Worth noting that we pass in something that has a serial style API though
physicaloven = MockArduino_OvenHost(ser[0])
physicaloven.start()

# Create the local proxy that is to be exposed by the web API - note that this passes in the serial port for the IOT object
# Not sure how that would work with real world physical things, but the communication approach would be the same
realoven = Oven(ser[1])              # Instantiate a thing to control

# Create the network proxy for the IOT object. Note this passes in the local proxy - to use it for local control

# Create and start the web interface
oveninterface = OvenInterface(realoven)
oveninterface.start()


#
# This should wait for the oven interface to have started and be ready.
#
# How the hell can it though?
#

# Create and start the mDNS service
port=5000
while True:
    try:
        ovenservice = OvenService(port=port)
        break
    except IOError:
        port += 1
        if port>6000:
          raise

print "STARTED ON PORT", port

ovenservice.start()

time.sleep(1)      # Wait 1 second for the system to be ready

# Create the interface that we would use as an end user piece of code for communicating to the oven remotely.
# In reality, this next line would be what would be part of "from kitchen import oven"


#############################################################################################
#
# EXAMPLE CLIENT SIDE CODE - NOTE IT RUNS A SCRIPT TO FOLLOW _ SETTING THE DEVICE TO TARGET
# TEMPERATURES, AND MONITORING CURRENT STATE
#
#############################################################################################

oven = oven_proxy("oven")

if len(sys.argv) > 1:
    print "*********************************************************************"
    print 
    print "Waiting before proceeding."
    print "You may want to find the service this way: avahi-browse -r -a|more"
    print 
    raw_input("press return when ready> ")
    #time.sleep(1000)

def alarm():
    print "Oven has reached temperature"

oven.target_temperature = 200
while oven.temperature  < oven.target_temperature:
    print "Heating to", oven.target_temperature, " Current Temp:", oven.temperature
    time.sleep(1)

alarm()

# Debugging
print "props(realoven)", props(realoven)
print "props(oven)", props(oven)

# This is the simulation
script = [
    [ 0, 180],
    [ 8, 250],
    [ 13, 100],
]
events = iter(script)
run_start = now = time.time()
upcoming = events.next()
finished_events = False

last_temp = oven.temperature                        # This is essentially what we want to write.

while True:
    if not finished_events:
        if (time.time()-run_start) >= upcoming[0]:
            # Time for this upcoming event to fire.
            oven.target_temperature = upcoming[1]   # This is essentially what we want to write. Not quite, but close.
            try:
                upcoming = events.next()
            except StopIteration:
                finished_events = True
            # Pre for next event
    else:
        if (time.time()-run_start) - upcoming[0] > 5:
            # Allow to run for 10 seconds after the last event, then terminate
            break

    curr_temp = oven.temperature                 # This is what we want to write, whether or not the API is actually over IP.
    current_target = oven.target_temperature     # This is what we want to write, whether or not the API is actually over IP.

    if last_temp != curr_temp:
        print int((time.time()-run_start)*100)/100.0, "Oven Temp:", curr_temp, "Oven Set To:", current_target
        last_temp = curr_temp
    time.sleep(0.01)
    now = time.time()



