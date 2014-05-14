#ifndef IOTOY_TEST_SUPPORT_MOCK_SERIAL_H
#define IOTOY_TEST_SUPPORT_MOCK_SERIAL_H

// Mock version of the Serial interface to allow testing of arduino code without using an arduino

#include <iostream>
#include <MockString.h>

class MockSerial {
  String serial_data;
  bool newline;
  bool debug;

public:
  void dump();
  MockSerial() : serial_data(""),debug(true),newline(true) { };
  ~MockSerial() {};
  void debug_on();
  void debug_off();
  void reset();
  void begin(int speed);
  void send_from_host(std::string arg);
  void print(std::string arg);
  void println(std::string arg);
  void print(int arg);
  void println(int arg);
  void println();
  int available();
  int read();
};

extern MockSerial Serial;

#define DEBUG_ON Serial.debug_on()
#define DEBUG_OFF Serial.debug_off()

/* Mock suite tests */
void basic_Serial_Diagnostic();
#endif
