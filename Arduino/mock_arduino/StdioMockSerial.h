#ifndef IOTOY_TEST_SUPPORT_STDIO_MOCK_SERIAL_H
#define IOTOY_TEST_SUPPORT_STDIO_MOCK_SERIAL_H

// Mock version of the Serial interface to allow testing of arduino code without using an arduino

#include <iostream>
#include <MockString.h>
#include <string.h>
#include <stdexcept>

class StdioMockSerial {
  String serial_data; // To device
  std::string serial_data_fromdevice;
  bool debug;
  bool newline;

public:
  void dump();            // Called by test runner to inspect buffers

  // Next two used by the c++ file to create/destroy default serial interface
  StdioMockSerial() : serial_data(""),serial_data_fromdevice(""),
                      debug(true),newline(true) { };
  ~StdioMockSerial() {};

  void debug_on();                       // Called by test runner to enable debugging
  void debug_off();                      // Called by test runner to disable debugging
  void send_from_host(std::string arg);  // Called by test runner to send data to the arduino sketch

  std::string recv_on_host();  // Called by test runner to recieve data from the arduino sketch
                               // This gives you all the data - warts and all.
                               // Error is signalled via an exception

  std::string recv_on_host(int count);   // Called by test runner to recieve data from the arduino sketch
                                         // This gives you a string of the specified length
                                         // Error is signalled via an exception

  std::string recvln_on_host(int count);   // Optimistic - this gives you a line of text from the client
                                           // Error is signalled via an exception

  // Gap - no "recv on host" - to recieve data from the arduino sketch for output
  // Do we need that? Would be useful for automation testing

  void reset();                  // Called by the Arduino Sketch to reset the interface - empties buffer
  void begin(int speed);         // Called by the Arduino Sketch to set serial speed
  void print(std::string arg);   // Called by the Arduino Sketch to send arg to serial comms
  void println(std::string arg); // Called by the Arduino Sketch to send arg + "\n" to serial comms 
  void print(int arg);           // Called by the Arduino Sketch to send arg to serial comms
  void println(int arg);         // Called by the Arduino Sketch to send arg + "\n" to serial comms 
  void println();                // Called by the Arduino Sketch to "\n" to serial comms 
  int available();               // Called by the Arduino Sketch to see if data is available
  int read();                    // Called by the Arduino Sketch to read data
};

extern StdioMockSerial Serial;

#define DEBUG_ON Serial.debug_on()
#define DEBUG_OFF Serial.debug_off()

/* Mock suite tests */
void basic_Serial_Diagnostic();
#endif
