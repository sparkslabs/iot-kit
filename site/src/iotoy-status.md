---
template: mainpage
source_form: markdown
name: IOToy Status
updated: July 2015
title: IOToy Status
---
## IOToy Status

The short version is that IOToy is stable, and useful.

It has been used with SumoBots, and in the prototype [BBC Micro:bit][MICROBIT]

There are likely to be tweaks to the serial API in future including:

* The ability to specify and pass in multiple arguments to functions
* The ability to subscribe to updates to values - to allow the device to push data

Similarly are likely to be tweaks to the serial API in future including:

* The ability to use websockets to stream values. From a semantic perspective,
  this will be modelled linguistically as a channel - but in an actor model
  style rather than CSP.

--- 
This is a new site (as of July 2015), and the Status for IOToy will be copied over into here.
For the moment, it's best to look at the specs on the IOToy github repo:

* <https://github.com/sparkslabs/iotoy>

[MICROBIT]: http://www.bbc.co.uk/rd/blog/2015/07/prototyping-the-bbc-microbit
