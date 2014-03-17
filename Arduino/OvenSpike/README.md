Oven Spike
==========

Um, an oven. Really? Really??!

Yes. The reason for an oven is as follows:

* An oven is a real world device that (in the form of a microwave/convection combi) is programmed with a target temp and time
* It has a real world state (a temperature)
* It generally has a real world target - a target temperature
* It can either be switched on or off.

In this case it was used to think through a bunch of different ideas for the serial based API.

This isn't really so very different from Servos moving to specific positions etc.

### Some Notes ###

This files in this directory are examples at present, implementing the basic API.

For the moment, these are all examples, rather than a generic API

OvenHostTinyTest.ino
   - This compiles small enough to fit onto (and run correctly) on an Ardunio Atmega 8A - 8K Flash, 1K Ram.
   - Note that this uses deprecated conversions string constants to char*, this is "OK
     in the arduino dev envioronment, but out of kilter for standard C++

OvenHost.ino
   - This uses the CommandHostCore.cpp file above to implement a basic "thing" - which in this case
     is an oven control.

host_test.cpp
   - This is a simple harness that can include an ino file, and provide a basic mock arduino environment for
     running arduino sketches. This includes the capability of providing a mock serial interface into which
     we can inject strings.

The directory above contains the following files:

CommandHostCore.cpp
   - This is a source library for use with normal Arduino devices - such as those with 32K of memory.
   - This uses Arduino String class functions that cost you about 3K of flash, but are easier to work with
     over char *

CommandHostTiny.cpp
   - This is a source library for use with constrained Arduino devices - such as Ardunio Atmega 8A 
   - It's slightly harder to work with, but works work well on constrained devices.

Things that might be useful:

   - A command wrapper for .ino scratch files. This would allow the serial console to be simulated by
     stdin and stdout.



