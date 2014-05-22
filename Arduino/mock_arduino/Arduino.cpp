#ifndef IOTOY_TEST_SUPPORT_MOCK_ARDUINO_H
#define IOTOY_TEST_SUPPORT_MOCK_ARDUINO_H

#include <Arduino.h>
#include <iostream>

void delay(int t) {
#ifdef TRACING
  std::cout << "DELAY NOT IMPLEMENTED YET, time " << t << std::endl;
#endif
}

int analogRead(int pin) { return 128; }
int map(int val, int min_a, int max_a, int min_b, int max_b) { return 128; }

void analogWrite(int, int) { }
void digitalWrite(int, int) { }
void pinMode(int , int) { }

const char * F(const char * passthrough) {
  return passthrough;
}

#endif

