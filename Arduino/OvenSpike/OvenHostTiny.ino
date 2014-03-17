// This next part should be ifdef'd appropriately

//  #include "Servo.h"

#ifdef LOCALTEST
#include "../test_support/MockServo.h"
#else
#include "Servo.h"
#endif

#include "../CommandHostTiny.cpp"

class OvenHost : public CommandHost {
private:
  int temperature;
  int target_temperature;
char temp_str[128];
public:
  OvenHost() : temperature(20), target_temperature(21) {}
  ~OvenHost() {}


  const char * attrs() {
    return "temperature:int,target_temperature:int";
  }
  const char * funcs() { // need to implement on/off(!)
    return "set_target_temp,on,off";
  }
  bool has_help(char * name) {
    if (strcmp(name,"temperature")==0) return true;
    if (strcmp(name,"target_temperature")==0) return true;
    if (strcmp(name,"on")==0) return true;
    if (strcmp(name,"off")==0) return true;
    return false;
  }
  const char *help(char * name) {
    if (strcmp(name,"temperature")==0) return "Current temperature of the oven.";
    if (strcmp(name,"target_temperature")==0) return "Target temperature of the oven.";
    if (strcmp(name,"on")==0) return "Function that turns the oven on";
    if (strcmp(name,"off")==0) return "Function that turns the oven off";
    return "-";
  }
  bool exists(char * attribute) {
    if (strcmp(attribute,"temperature")==0) return true;
    if (strcmp(attribute,"target_temperature")==0) return true;
    return false;
  }
  const char *get(char * attribute) {
    if (strcmp(attribute,"temperature")==0) { itoa (temperature, temp_str, 10); return temp_str; }
    if (strcmp(attribute,"target_temperature")==0) { itoa (target_temperature, temp_str, 10); return temp_str; }
    return "-";
  }
  int set(char* attribute, char* raw_value) {
    if (strcmp(attribute,"temperature")==0) {
      int value = atoi(raw_value);
      temperature = value;
      return 200;
    }
    if (strcmp(attribute,"target_temperature")==0) {
      int value = atoi(raw_value);
      target_temperature = value;
      return 200;
    }
    return 404;
  }
};

OvenHost MyCommandHost;
// Servo myservo1;  // create servo object to control a servo 
// Servo myservo2;  // create servo object to control a servo 
// Servo myservo3;  // create servo object to control a servo 

// int potpin = 0;  // analog pin used to connect the potentiometer
// int val;    // variable to read the value from the analog pin 

void setup() {
  Serial.begin(9600);

  Serial.print("DEVICE ");
  Serial.print("OVEN "); // Name of the device. May or may note be used on the network verbatim.
  // Do I want some sort of Mac Address here? If so, how? How to make unique to the device?
  // Or /sufficiently/ unique?
  Serial.println("OK");
//   myservo1.attach(9);  // attaches the servo on pin 9 to the servo object 
//   myservo2.attach(10);  // attaches the servo on pin 9 to the servo object 
//   myservo3.attach(11);  // attaches the servo on pin 9 to the servo object 

}

void loop() {
  MyCommandHost.run_host();
//   val = analogRead(potpin);            // reads the value of the potentiometer (value between 0 and 1023) 
//   val = map(val, 0, 1023, 0, 179);     // scale it to use it with the servo (value between 0 and 180) 
//  myservo1.write(val);                  // sets the servo position according to the scaled value 
//  delay(15);                           // waits for the servo to get there 
}

