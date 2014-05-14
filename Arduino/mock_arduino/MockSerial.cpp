
// Mock version of the Serial interface to allow testing of arduino code without using an arduino
#include <MockSerial.h>

#include <iostream>
// #include <MockString.h>

MockSerial Serial;

  void MockSerial::dump() {
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
  void MockSerial::debug_on() {
    debug = true;
    std::cout << "Debug enabled" << std::endl;
  }
  void MockSerial::debug_off() {
    debug = false;
    std::cout << "Disabling debug" << std::endl;
  }
  void MockSerial::reset() {
    if (debug) {
      std::cout << "SERIAL_DEBUG: Serial reset" << std::endl;
    }
    serial_data = "";
  }
  void MockSerial::begin(int speed) {
    if (debug) {
      std::cout << "SERIAL_DEBUG: Serial, speed set to " << speed << std::endl;
    }
  }
  void MockSerial::send_from_host(std::string arg) {
    if (debug) {
      std::cout << "SERIAL_DEBUG: >> : " << arg << std::endl;
    }
    serial_data = serial_data + (String(arg.c_str()));
  }
  void MockSerial::print(std::string arg) {
    if (debug) {
      if (newline){
        std::cout << "SERIAL_DEBUG: << : ";
      }
      std::cout << arg;
      newline = false;
    }
  }
  void MockSerial::println(std::string arg) {
    if (debug) {
      if (newline){
        std::cout << "SERIAL_DEBUG: << : ";
      }
      std::cout << arg << std::endl;
      newline = true;
    }
  }
  void MockSerial::print(int arg) {
    std::cout << arg;
  }
  void MockSerial::println(int arg) {
    std::cout << arg << std::endl;
  }
  void MockSerial::println() {
    std::cout << std::endl;
  }
  int MockSerial::available() { // Mock Serial makes one byte available at a time
    return serial_data.length();
  }
  int MockSerial::read() {
      int result = serial_data[0];
      serial_data = serial_data.substring(1);
      return result;

  }

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
