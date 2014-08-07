// Robot Spoke for a constrained device

#include <CommandHostTiny.h>

const int DRIVE_FORWARD_TIME_MS = 1500;
const int TURN_TIME_MS = 2000;

class TestHost : public CommandHostTiny {
private:
  int drive_forward_time_ms; // Advertised attribute - type int
  int turn_time_ms;          // Advertised attribute - type int

  char str_id[32];           // Advertised attribute - type char* (str)
  double ratio;              // Advertised attribute - type double
  bool some_flag;            // Advertised attribute - type bool

  char temp_str[128];
public:
  TestHost() : drive_forward_time_ms(DRIVE_FORWARD_TIME_MS), turn_time_ms(TURN_TIME_MS), ratio(0), some_flag(true) {
      strcpy(str_id, "default");
  }
  ~TestHost() { }

  const char *hostid() { 
    return "testhosttiny";
  }

  const char * attrs() {
    return "drive_forward_time_ms:int,turn_time_ms:int,str_id:str,ratio:float,some_flag:bool";
  }
  const char * funcs() {
    return "barecommand,one_arg_int,one_arg_bool,one_arg_str,one_arg_float,one_arg_T,no_arg_result_int,no_arg_result_bool,no_arg_result_str,no_arg_result_float,no_arg_result_T,one_arg_int_result_int";
  }

  bool has_help(char * name) {
    if (strcmp(name,"drive_forward_time_ms")==0) return true;
    if (strcmp(name,"turn_time_ms")==0) return true;

    if (strcmp(name,"ratio")==0) return true;
    if (strcmp(name,"some_flag")==0) return true;
    if (strcmp(name,"str_id")==0) return true;

    if (strcmp(name,"one_arg_int")==0) return true;
    if (strcmp(name,"one_arg_bool")==0) return true;
    if (strcmp(name,"one_arg_str")==0) return true;
    if (strcmp(name,"one_arg_float")==0) return true;
    if (strcmp(name,"one_arg_T")==0) return true;
    if (strcmp(name,"barecommand")==0) return true;

    if (strcmp(name,"no_arg_result_int")==0) return true;
    if (strcmp(name,"no_arg_result_bool")==0) return true;
    if (strcmp(name,"no_arg_result_str")==0) return true;
    if (strcmp(name,"no_arg_result_float")==0) return true;
    if (strcmp(name,"no_arg_result_T")==0) return true;

    if (strcmp(name,"one_arg_int_result_int")==0) return true;

    return false;
  }

  void help(char * name) {
    if (strcmp(name,"drive_forward_time_ms")==0) Serial.println(F("int - How long to move forward"));
    else if (strcmp(name,"turn_time_ms")==0) Serial.println(F("int - How long to turn"));

    else if (strcmp(name,"ratio")==0) Serial.println(F("float - Sample float attribute"));
    else if (strcmp(name,"some_flag")==0) Serial.println(F("bool - Sample bool attribute"));
    else if (strcmp(name,"str_id")==0) Serial.println(F("str - Sample str attribute"));

    else if (strcmp(name,"barecommand")==0) Serial.println(F("barecommand -> - test, basic command, no arg/result"));
    else if (strcmp(name,"one_arg_int")==0) Serial.println(F("one_arg_int myarg:int -> - test, one arg, integer"));
    else if (strcmp(name,"one_arg_bool")==0) Serial.println(F("one_arg_bool myarg:bool -> - test, one arg, boolean"));
    else if (strcmp(name,"one_arg_str")==0) Serial.println(F("one_arg_str myarg:str -> - test, one arg, string"));
    else if (strcmp(name,"one_arg_float")==0) Serial.println(F("one_arg_float myarg:float -> - test, one arg, float"));
    else if (strcmp(name,"one_arg_T")==0) Serial.println(F("one_arg_T attr:T -> - test, one arg, generic type"));

    else if (strcmp(name,"no_arg_result_int")==0) Serial.println(F("no_arg_result_int -> result:int - test, one arg, integer"));
    else if (strcmp(name,"no_arg_result_bool")==0) Serial.println(F("no_arg_result_bool -> result:bool - test, one arg, boolean"));
    else if (strcmp(name,"no_arg_result_str")==0) Serial.println(F("no_arg_result_str -> result:str - test, one arg, string"));
    else if (strcmp(name,"no_arg_result_float")==0) Serial.println(F("no_arg_result_float -> result:float - test, one arg, float"));
    else if (strcmp(name,"no_arg_result_T")==0) Serial.println(F("no_arg_result_T -> result:T - test, one arg, generic type"));

    else if (strcmp(name,"one_arg_int_result_int")==0) Serial.println(F("one_arg_int_result_int myarg:int -> result:int - test, one arg, one result, both ints"));
    else Serial.println(F("-"));
  }

  int no_arg_result_int() { strcpy(result_string, "100"); return 200; }
  int no_arg_result_bool() { strcpy(result_string, "True"); return 200; }
  int no_arg_result_str() { strcpy(result_string, "hello"); return 200; }
  int no_arg_result_float() { strcpy(result_string, "1.1"); return 200; }
  int no_arg_result_T() { strcpy(result_string, "4j2"); return 200; }

  bool exists(char * attribute) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) return true;
    if (strcmp(attribute,"turn_time_ms")==0) return true;
    if (strcmp(attribute,"ratio")==0) return true;
    if (strcmp(attribute,"some_flag")==0) return true;
    if (strcmp(attribute,"str_id")==0) return true;
    return false;
  }

  const char *get(char * attribute) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) { 
      itoa (drive_forward_time_ms, temp_str, 10); 
      return temp_str; 
    }
    if (strcmp(attribute,"turn_time_ms")==0) { 
      itoa (turn_time_ms, temp_str, 10); 
      return temp_str; 
    }
    if (strcmp(attribute,"str_id")==0) {
      return str_id;
    }
    if (strcmp(attribute,"ratio")==0) {
      ftoa(temp_str, ratio);
      return temp_str; 
    }
    if (strcmp(attribute,"some_flag")==0) { 
      if (some_flag) return "True";
      return "False";
    }
    return "-";
  }

  int set(char* attribute, char* raw_value) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) {
      int value = atoi(raw_value);
      drive_forward_time_ms = value;
      return 200;
    }
    if (strcmp(attribute,"turn_time_ms")==0) {
      int value = atoi(raw_value);
      turn_time_ms = value;
      return 200;
    }
    if (strcmp(attribute,"ratio")==0) { 
      double value = atof(raw_value);
      ratio = value;
      return 200;
    }
    if (strcmp(attribute,"some_flag")==0) {
      if (strcmp(raw_value,"True")==0) {
        some_flag=true;
        return 200;
      }
      if (strcmp(raw_value,"False")==0) {
        some_flag=false;
        return 200;
      }
      return 500;
    }
    if (strcmp(attribute,"str_id")==0) { 
      strncpy ( str_id, raw_value, 31 );
      str_id[31] = '\0';   // null character manually added
      return 200;
    }
    return 404;
  }

  int one_arg_int_result_int(char *raw_value) {
      int value = atoi(raw_value);
      itoa (value, result_string, 10);
      return 200;
  }

  int callfunc(char* funcname, char* raw_args) { 
    // Since this is a test host, it doesn't actually do anything
    if (strcmp(funcname,"no_arg_result_int")==0) { no_arg_result_int(); return 200; }
    if (strcmp(funcname,"no_arg_result_bool")==0) { no_arg_result_bool(); return 200; }
    if (strcmp(funcname,"no_arg_result_str")==0) { no_arg_result_str(); return 200; }
    if (strcmp(funcname,"no_arg_result_float")==0) { no_arg_result_float(); return 200; }
    if (strcmp(funcname,"no_arg_result_T")==0) { no_arg_result_T(); return 200; }
    if (strcmp(funcname,"one_arg_int_result_int")==0)  { one_arg_int_result_int(raw_args); return 200; }

    return 404;
  }

  void setup(void) {
      // Setup the pins
      CommandHostTiny::setup();
  }
};

TestHost MyCommandHost;

//----------------------------------------------------------
void setup()
{
  MyCommandHost.setup();
}

//----------------------------------------------------------
void loop()
{
  MyCommandHost.run_host();
}
