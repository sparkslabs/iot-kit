IOToy Arduino Files
===================

Manual Installation
-------------------

If you copy the directories in libraries into your arduino library
directory, you will find some new examples in your arduino IDE, and
also some extra libraries will be available.

Status: tested, good

Ubuntu / Debian packaging
-------------------------

To build a Debian package on your machine, type:

   make deb

To then use this package you can type:

   make use

This calls dpkg for you.

You can then start up the arduino ide as normal.

Ubuntu status: tested, good

Windows / Mac packaging
-----------------------

A zip file suitable for installing via the arduino ide exists here:

To install it, you choose the menu option:

    thing->thing->ba ding

You then need to restart the arduino ide

Windows status: untested
Mac status: untested


Use with MSP430 Energia Toolkit
-------------------------------
This set of code *has* been tested with the port of the arduino
IDE to the MSP430 platform, specifically with the MSP430 launchpad,
and the 'tiny' version of the codebase works with this. The packaging
however has not been tested.

Feedback welcome.

Usage
=====










