
// Mock version of the Serial interface to allow testing of arduino code without using an arduino
#include <StdioMockSerial.h>
#include <sstream>

StdioMockSerial Serial;

void StdioMockSerial::dump() {
  // Ignores debug flag, since what the point of looking at it when dumping the serial contents
  unsigned int size = serial_data.length()+1;
  if (size == 0) {
    if (debug) {
      std::cout << "SERIAL_DEBUG: Mock Serial empty." << std::endl;
    }
  } else {
    if (debug) {
      unsigned char * bytes = (unsigned char *) malloc(size);
      serial_data.getBytes(bytes, size);
      std::cout << "SERIAL_DEBUG: Mock Serial Dump:" << bytes << std::endl;
    }
  }
}
void StdioMockSerial::debug_on() {
  debug = true;
  std::cout << "Debug enabled" << std::endl;
}

void StdioMockSerial::debug_off() {
  debug = false;
//   std::cout << "Disabling debug" << std::endl;
}

void StdioMockSerial::reset() {
  if (debug) {
    std::cout << "SERIAL_DEBUG: Serial reset" << std::endl;
  }
  serial_data = "";
  serial_data_fromdevice = "";
}

void StdioMockSerial::begin(int speed) {
  if (debug) {
    std::cout << "SERIAL_DEBUG: Serial, speed set to " << speed << std::endl;
  }
}

void StdioMockSerial::send_from_host(std::string arg) {
  if (debug) {
    std::cout << "SERIAL_DEBUG: >> : " << arg << std::endl;
  }
  serial_data = serial_data + (String(arg.c_str()));
}

void StdioMockSerial::print(std::string arg) {
  if (debug) {
    if (newline){
      std::cout << "SERIAL_DEBUG: ";
    }
    std::cout << arg;
    newline = false;
  }
  serial_data_fromdevice = serial_data_fromdevice + arg;
}

void StdioMockSerial::println(std::string arg) {
  if (debug) {
    if (newline){
      std::cout << "SERIAL_DEBUG: << : ";
    }
    std::cout << arg << std::endl;
    newline = true;
  }
  serial_data_fromdevice = serial_data_fromdevice + arg + "\n";
}

void StdioMockSerial::print(int arg) {
  std::stringstream ss;
  ss << arg;
  if (debug) {
    std::cout << arg;
  }
  serial_data_fromdevice = serial_data_fromdevice + std::string(ss.str());
}


void StdioMockSerial::println(int arg) {
  if (debug) {
    std::cout << arg << std::endl;
  }
  std::stringstream ss;
  ss << arg;
  serial_data_fromdevice = serial_data_fromdevice + std::string(ss.str());
}

void StdioMockSerial::println() {
  if (debug) {
    std::cout << std::endl;
  }
  serial_data_fromdevice = serial_data_fromdevice + "\n";
}

int StdioMockSerial::available() { // Mock Serial makes one byte available at a time
  return serial_data.length();
}

int StdioMockSerial::read() {
    int result = serial_data[0];
    serial_data = serial_data.substring(1);
    return result;
}

// Called by test runner to recieve data from the arduino sketch
// This gives you ALL the data - warts and all.
// Error is signalled via an exception
std::string StdioMockSerial::recv_on_host() {

  if (serial_data_fromdevice.length() == 0) {
    throw std::runtime_error("You broke it. Keep both halves");
  }
  std::string result = serial_data_fromdevice;
  serial_data_fromdevice = "";
  return result;
}

// Called by test runner to recieve data from the arduino sketch
// This gives you a string of the specified length
// Error is signalled via an exception
std::string StdioMockSerial::recv_on_host(int count) {
  return "";
}

// Optimistic - this gives you a line of text from the client
std::string StdioMockSerial::recvln_on_host(int count) {
  return "";
}

/* Mock suite tests */
void basic_Serial_Diagnostic() {
    DEBUG_OFF;
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
