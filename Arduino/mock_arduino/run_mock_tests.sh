#!/bin/bash

echo "Cleaning test area"
rm -f *.o serial_test *~

echo "Building dependencies"
g++ -DSTDIOMOCKSERIAL -I. -c serial_test.cpp
g++ -DSTDIOMOCKSERIAL -I. -c Arduino.cpp
g++ -DSTDIOMOCKSERIAL -I. -c StdioMockSerial.cpp
g++ -DSTDIOMOCKSERIAL -I. -c MockString.cpp

echo "linking test app"
g++ serial_test.o Arduino.o StdioMockSerial.o MockString.o -o serial_test

echo "running test"
./serial_test

rm -f *.o serial_test
