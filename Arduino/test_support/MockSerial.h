
// Mock version of the Serial interface to allow testing of arduino code without using an arduino

#include <iostream>
#include "MockString.h"

class MockSerial {
  String serial_data;
  bool newline;
  bool debug;

public:
  void dump() {
    // Ignores debug flag, since what the point of looking at it when dumping the serial contents
    unsigned int size = serial_data.length()+1;
    if (size == 0) {
        std::cout << "SERIAL_DEBUG: Mock Serial empty." << std::endl;
    } else {
        unsigned char * bytes = (unsigned char *) malloc(size);
        serial_data.getBytes(bytes, size);
        std::cout << "SERIAL_DEBUG: Mock Serial Dump:" << bytes << std::endl;
    }
  }
  MockSerial() : serial_data(""),debug(true),newline(true) { };
  ~MockSerial() {};
  void debug_on() {
    debug = true;
    std::cout << "Debug enabled" << std::endl;
  }
  void debug_off() {
    debug = false;
    std::cout << "Disabling debug" << std::endl;
  }
  void reset() {
    if (debug) {
      std::cout << "SERIAL_DEBUG: Serial reset" << std::endl;
    }
    serial_data = "";
  }
  void begin(int speed) {
    if (debug) {
      std::cout << "SERIAL_DEBUG: Serial, speed set to " << speed << std::endl;
    }
  }
  void send_from_host(std::string arg) {
    if (debug) {
      std::cout << "SERIAL_DEBUG: >> : " << arg << std::endl;
    }
    serial_data = serial_data + (String(arg.c_str()));
  }
  void print(std::string arg) {
    if (debug) {
      if (newline){
        std::cout << "SERIAL_DEBUG: << : ";
      }
      std::cout << arg;
      newline = false;
    }
  }
  void println(std::string arg) {
    if (debug) {
      if (newline){
        std::cout << "SERIAL_DEBUG: << : ";
      }
      std::cout << arg << std::endl;
      newline = true;
    }
  }
  void print(int arg) {
    std::cout << arg;
  }
  void println(int arg) {
    std::cout << arg << std::endl;
  }
  void println() {
    std::cout << std::endl;
  }
  int available() { // Mock Serial makes one byte available at a time
    return serial_data.length();
  }
  int read() {
      int result = serial_data[0];
      serial_data = serial_data.substring(1);
      return result;

  }
};

MockSerial Serial;

#define DEBUG_ON Serial.debug_on()
#define DEBUG_OFF Serial.debug_off()

/* Mock suite tests */
void basic_Serial_Diagnostic() {
    Serial.reset();
    Serial.dump();
    std::cout << "Available:" << Serial.available() << std::endl;
    Serial.send_from_host("This is a simple test -- ");
    Serial.dump();
    Serial.send_from_host("This is another simple test -- ");
    Serial.dump();
    int count = 0; 
    std::cout << "Available:" << Serial.available() << std::endl;

    while (Serial.available()) {
      int next_char = Serial.read();
      count ++;
      std::cout << "CHAR : " << count << " : " << next_char << std::endl;
    }
    Serial.reset();
}
