
// Mock version of the Servo interface to allow testing of arduino code without using an arduino

#ifndef TEST_SUPPORT__MOCKSERVO_H
#define TEST_SUPPORT__MOCKSERVO_H

#include <iostream>

class Servo {
  int pin;
  int speed;
public:

  Servo() : pin(-1), speed(0) {
    std::cout << "Creating a servo!" << std::endl;
  }
  ~Servo() {
    std::cout << "Disposing of a servo!" << std::endl;
  } 
  void attach(int newpin) {
    pin = newpin;
  }
  void detach() {
    if (pin == -1) {
        std::cout << "Need to set servo first!" << std::endl;
    } else {
        std::cout << "Stopping servo on pin " << pin << " and detaching" << std::endl;
        speed = 0;
        pin = -1;
    }
  }
  void write(int value) {
    if (pin == -1) {
        std::cout << "Need to set servo first!" << std::endl;
    } else {
        std::cout << "Setting servo on pin " << pin << " to speed " << value << std::endl;
    }
    speed = value;
  }
};

#endif
