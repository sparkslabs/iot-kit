// Robot Spoke for a constrained device

#include <CommandHostTiny.h>

const int DRIVE_FORWARD_TIME_MS = 1500;
const int TURN_TIME_MS = 2000;

class TestHost : public CommandHostTiny {
private:
  int drive_forward_time_ms; // To be replaced
  int turn_time_ms;          // To be replaced
  char temp_str[128];
public:
  TestHost() : drive_forward_time_ms(DRIVE_FORWARD_TIME_MS), turn_time_ms(TURN_TIME_MS) { }
  ~TestHost() { }

  const char *hostid() { 
    return "sumobot";
  }

  const char * attrs() {
    return "drive_forward_time_ms:int,turn_time_ms:int";
  }

  const char * funcs() {
    return "barecommand,one_arg_int,one_arg_bool,one_arg_str,one_arg_float,one_arg_T,no_arg_result_int,no_arg_result_bool,no_arg_result_str,no_arg_result_float,no_arg_result_T,one_arg_int_result_int";
  }

  bool has_help(char * name) {
    if (strcmp(name,"drive_forward_time_ms")==0) return true;
    if (strcmp(name,"turn_time_ms")==0) return true;
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

  const char *help(char * name) {
    if (strcmp(name,"drive_forward_time_ms")==0) return "int - How long to move forward";
    if (strcmp(name,"turn_time_ms")==0) return "int - How long to turn";
    if (strcmp(name,"barecommand")==0) return "barecommand -> - test, basic command, no arg/result";
    if (strcmp(name,"one_arg_int")==0) return "one_arg_int myarg:int -> - test, one arg, integer";
    if (strcmp(name,"one_arg_bool")==0) return "one_arg_bool myarg:bool -> - test, one arg, boolean";
    if (strcmp(name,"one_arg_str")==0) return "one_arg_str myarg:str -> - test, one arg, string";
    if (strcmp(name,"one_arg_float")==0) return "one_arg_float myarg:float -> - test, one arg, float";
    if (strcmp(name,"one_arg_T")==0) return "one_arg_T attr:T -> - test, one arg, generic type";

    if (strcmp(name,"no_arg_result_int")==0) return "no_arg_result_int -> result:int - test, one arg, integer";
    if (strcmp(name,"no_arg_result_bool")==0) return "no_arg_result_bool -> result:bool - test, one arg, boolean";
    if (strcmp(name,"no_arg_result_str")==0) return "no_arg_result_str -> result:str - test, one arg, string";
    if (strcmp(name,"no_arg_result_float")==0) return "no_arg_result_float -> result:float - test, one arg, float";
    if (strcmp(name,"no_arg_result_T")==0) return "no_arg_result_T -> result:T - test, one arg, generic type";

    if (strcmp(name,"one_arg_int_result_int")==0) return "one_arg_int_result_int -> result:int - test, one arg, one result, both ints";
    return "-";
  }

  bool exists(char * attribute) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) return true;
    if (strcmp(attribute,"turn_time_ms")==0) return true;
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
    return 404;
  }

  int callfunc(char* funcname, char* raw_args) { 
    // Since this is a test host, it doesn't actually do anything
    return 200;
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

