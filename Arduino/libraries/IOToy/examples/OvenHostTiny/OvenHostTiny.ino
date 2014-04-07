// Oven Spike for constrained devices

#include <CommandHostTiny.cpp>

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

void setup() {
  Serial.begin(9600);

  Serial.print("DEVICE ");
  Serial.print("OVEN ");
  Serial.println("OK");

}

void loop() {
  MyCommandHost.run_host();
}

