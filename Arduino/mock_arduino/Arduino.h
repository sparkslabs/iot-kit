#ifndef IOTOY_TEST_SUPPORT_MOCK_ARDUINO_H
#define IOTOY_TEST_SUPPORT_MOCK_ARDUINO_H

#ifdef STDIOMOCKSERIAL
#include <StdioMockSerial.h>
#else
#include <MockSerial.h>
#endif

#include <MockServo.h>
// #i n c l u d e <MockString.cpp>
#include <MockString.h>

#define HIGH 1
#define LOW 1
#define OUTPUT 1

#include <stdlib.h>

/* Other arduino & debug support functions */

void delay(int t);

int analogRead(int pin);
int map(int val, int min_a, int max_a, int min_b, int max_b);
void analogWrite(int, int);
void digitalWrite(int, int);
void pinMode(int , int);

const char * F(const char * passthrough);

#endif

