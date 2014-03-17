
#include "../CommandHostCore.cpp"

class OvenHost : public CommandHost {
private:
  int temperature;
  int target_temperature;

public:
  OvenHost() {}
  ~OvenHost() {}
  String attrs() {
    return String("temperature:int,target_temperature:int");
  }
  String funcs() {
    return String("set_target_temp,on,off");
  }
  bool has_help(String name) {
    if (name == "temperature") return true;
    if (name == "target_temperature") return true;
    if (name == "on") return true;
    if (name == "off") return true;
    return false;
  }
  String help(String name) {
    if (name == "temperature") return String("The current temperature of the oven. Not directly modifiable.");
    if (name == "target_temperature") return String("The target temperature of the oven. Directly modifiable.");
    if (name == "on") return String("Function that turns the oven on");
    if (name == "off") return String("Function that turns the oven off");
    return String("-");
  }
  bool exists(String attribute) {
    if (attribute == "temperature") return true;
    if (attribute == "target_temperature") return true;
    return false;
  }
  String get(String attribute) {
    if (attribute == "temperature") return String(temperature);
    if (attribute == "target_temperature") return String(target_temperature);
    return String("-");
  }
  int set(String attribute, String raw_value) {
    if (attribute == "temperature") {
      int value = raw_value.toInt();
      temperature = value;
      return 200;
    }
    if (attribute == "target_temperature") {
      int value = raw_value.toInt();
      target_temperature = value;
      return 200;
    }
    return 404;
  }
};

OvenHost MyCommandHost;

void setup() {
  Serial.begin(9600);
  Serial.print("DEVICE ");
  Serial.print("OVEN "); // Name of the device. May or may note be used on the network verbatim.
                         // Do I want some sort of Mac Address here? If so, how? How to make unique to the device?
                         // Or /sufficiently/ unique?
  Serial.println("READY");
}

void loop() {
//   MyCommandHost.buffer_serial();
  MyCommandHost.run_host();
}