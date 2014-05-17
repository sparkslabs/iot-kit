/*

The reason this doesn't use "make" is to avoid a clash with the way this directory is
intended to be used. Yes, it's suboptimal, but it's intended to bootstrap a decent
testing process, and will probably disappear at some point. (famous last words)

*/

#include <iostream>
#include <Arduino.h>


int main(int argc, char *argv[]) {
    std::cout << "==================== Starting tests ====================" << std::endl;

  DEBUG_OFF;
    Serial.reset();
    Serial.dump();

    Serial.print("Hello World");
    std::string data = Serial.recv_on_host();
    std::cout << "Data from device:" << data << ":" << std::endl;

    Serial.reset();
    Serial.println("Hello World");
    std::string data2 = Serial.recv_on_host();
    std::cout << "Data from device:" << data2 << ":" << std::endl;

    Serial.reset();
    Serial.println();
    std::string data3 = Serial.recv_on_host();
    std::cout << "Data from device:" << data3 << ":" << std::endl;

    Serial.reset();
    Serial.print(123456);
    std::string data4 = Serial.recv_on_host();
    std::cout << "Data from device:" << data4 << ":" << std::endl;

    Serial.reset();
    Serial.println(123456);
    std::string data5 = Serial.recv_on_host();
    std::cout << "Data from device:" << data5 << ":" << std::endl;

    Serial.reset();
    // Purges the contents of the Serial device.

    try {
      Serial.recv_on_host();
    }
    catch (std::runtime_error &e) {
      std::cout << "Expected Fail (good): " << e.what() << std::endl;
    }

    std::cout << "==================== Tests complete. ====================" << std::endl;
    std::cout << std::endl << std::endl;
    std::cout << "******************** Running Serial Diagnostics ********************" << std::endl;
    basic_Serial_Diagnostic();
    std::cout << "********************Diagnostics complete ********************" << std::endl;
  return 0;
}
