#!/bin/bash

echo >&2 "Cleaning test area"
rm -f *.o stdio_host *~

echo >&2 "Building dependencies"
g++ -g -DTESTING -DSTDIOMOCKSERIAL -I. -I../libraries/IOToy -c ../libraries/IOToy/CommandHostTiny.cpp
g++ -g -DTESTING -DSTDIOMOCKSERIAL -I. -I../libraries/IOToy -c stdio_host.cpp
g++ -g -DTESTING -DSTDIOMOCKSERIAL -I. -I../libraries/IOToy -c Arduino.cpp
g++ -g -DTESTING -DSTDIOMOCKSERIAL -I. -I../libraries/IOToy -c StdioMockSerial.cpp
g++ -g -DTESTING -DSTDIOMOCKSERIAL -I. -I../libraries/IOToy -c MockString.cpp

echo >&2 "linking test app"
g++ -g stdio_host.o CommandHostTiny.o Arduino.o StdioMockSerial.o MockString.o -o stdio_host

echo >&2 "Testing Host"
echo >&2 "how we actually do this is TBD"

# Note: The stdio_host can self terminate under
# the following conditions:
#  * The code calls Serial.shutdown() - not recommended
#  * The test harness closes stdin - eg like in a pipe
#  * The command line sends a EOF / control D via char code 4
echo; echo "Func test --------------------------------------------"
( echo "ping" ;
  echo "help" ;
  echo "help help" ;
  echo "funcs" ;
  echo "attrs" ;
  echo "help ping" ;
  echo "help funcs" ;
  echo "help attrs" ;
  echo "help set" ;
  echo "help get" ;
) |./stdio_host

echo; echo "bogus command test ------------------------------------"
echo "hello" |./stdio_host ## This (no longer) causes a crash! :-)

echo; echo "bogus function test --------------------------------------------"
echo "hello world" |./stdio_host ## This (no longer) causes a crash! :-)

echo; echo "bogus function test --------------------------------------------"
echo "set flibble" |./stdio_host ## This currently causes a crash! ...

echo >&2 "tests complete, leaving the binary here, cleaning rest"
rm -f *.o
