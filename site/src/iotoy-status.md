---
template: mainpage
source_form: markdown
name: IOT-Kit Status
updated: Feb 2018
title: IOToy Status
---
## IOT-Kit Status

The short version is that IOT-Kit is stable, and useful.

It has been used with SumoBots, and in the prototype [BBC Micro:bit][MICROBIT]

There are likely to be tweaks to the serial API in future including:

* The ability to specify and pass in multiple arguments to functions
* The ability to subscribe to updates to values - to allow the device to push data

Similarly are likely to be tweaks to the serial API in future including:

* The ability to use websockets to stream values. From a semantic perspective,
  this will be modelled linguistically as a channel - but in an actor model
  style rather than CSP.

--- 
More detail:

* <https://github.com/sparkslabs/iot-kit/>

[MICROBIT]: http://www.bbc.co.uk/rd/blog/2015/07/prototyping-the-bbc-microbit
