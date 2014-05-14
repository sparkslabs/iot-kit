IOTOY Python
============
This is the collection of IOToy modules and experiments built. It will get tidied up ASAP.


########################################################################
#
# Example Code/ Test Harness, consists of two halves:
#    * Set up the test IOT object services etc
#    * Client side code that monitors the oven and makes it change
#      temperatures at given times.
#
# Currently Missing:
#    * __call__ - mapping to post
#    * Object data model - based on jsonpickle & .well-known / meta
#      ideas & JSON HOME proposed standard
#    * Non-local external proxy via httptunnel or similar.
#      (easy to bolt on, but needs integrating)
#    * Websockets for data subscribe / data publish
#      - To be represented as channels (active queues) with callbacks
#
#######################################################################

The iotoy/spike.py file has now been split up into the following pieces
instead:

    .
    ├── __init__.py
    ├── webinterface.py
    ├── discovery.py
    ├── value_types.py
    ├── dummyserial.py
    ├── utils.py
    └── oven_spike
        ├── arduino_proxy.py
        ├── __init__.py
        ├── mdns_web_service.py
        ├── mock_arduino.py
        └── oven_client.py

There are chunks of the oven spike which could be and should be generalised
now - in particular to allow a non-crafted version of the API. In many
respects the mock_arduino ovent host should itself really be split in two
one part mock in the iotoy/ directory and one part application mock in
the examples directory.
