IOToy - An IOT Stack for Toys
=============================

This is where a collection of tools for creating and working with toys
connected to each other as *an* Internet of Toys. The following pieces
are in the process of being packaged up to go in here:

* A collection of pieces allowing serial control (wired or BT) and
  introspection of an arduino device.
* A mapping of that to a python proxy
* A mapping of that python proxy to a RESTful JSON based service.
* Automatic advertisement of that service on a local mDNS interface -
  with the service name derived from the arduino API
* A python API for "importing" IOT devices. In particular treating
  devices like python packages.
* A python API for then mapping the RESTful interface back to python
  linguistic rules.

The idea being that you can build your own little robots or sensors.
Once you've done that being able to do the minimum to allow it to be
controlled using high level python code over a local network connection
doing something like this:

    from home import robot

    ON = 1
    robot.forward()
    robot.led = ON
    if robot.sensor >255:
       robot.forward()

    print robot.sensor.__doc__

### Linguistic mapping of REST ###

The last thing that this project seeks to do is to implement something
RPC/SOAP like. Instead, this project works on the following assumptions.

In python:

    >>> x = module.SomeThing()
    >>> x
    <module.SomeThing object at 0xa11c44c>

In this it should be clear that in python you don't actually ever represent
with the actual hardware or data - just representations, and interact with
them via names. In particular, <code>SomeThing()</code> creates a resource,
which has a given representation. We can give that representation a
name - <code>x</code>.

From then on, we can do things like:

    >>> x.name = "Frank"
    >>> x.name
    'Frank'

In this case, <code>x.\_\_setattr_\_("name", "Frank")</code> sets a given
name to map to a given representation of bytes. Similarly the second like
performs <code>x.\_\_getattr_\_("name")</code>.

From this view, you can have the following mappings:

* <code>x</code> maps can be viewed as mapping to a web server
* <code>.name</code> can map to a given resource - eg <code>/names</code>
* <code>x.\_\_setattr_\_("name", "Frank")</code> is akin to <code>PUT /name HTTP/1.0 "Frank"</code>
* <code>x.\_\_getattr_\_("name")</code> is akin to <code>GET /name HTTP/1.0</code>
* Perhaps less obviously, <code>module.SomeThing()</code> maps:
    * module to a web server
    * <code>SomeThing</code> to a resource - most obviously <code>/SomeThing</code>
    * <code>module.SomeThing()</code> maps to <code>POST /SomeThing HTTP/1.0 _empty body_</code>


### License ###

The code in this release will all be under the Apache 2 Licence, with
an option to allow reuse under the GPL version 2.

Original implementations ©copyright 2013 BBC.


### Contact ###

Michael Sparks

twitter: @sparks_rd
website: http://www.sparkslabs.com/michael/
email: sparks DOT m AT gmail

