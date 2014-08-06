
#include <CommandHostTiny.h>
#include <Arduino.h>

  const char * CommandHostTiny::hostid() { return "iotoy_1"; }
  void CommandHostTiny::help(char * name) {  }
  const char * CommandHostTiny::attrs() { return ""; }
  const char * CommandHostTiny::funcs() { return ""; }
  bool CommandHostTiny::exists(char * attribute) { return false; }
  bool CommandHostTiny::has_help(char * name) { Serial.println(name); return false; }
  const char * CommandHostTiny::get(char * attribute) { return "-"; }
  int CommandHostTiny::set(char* attribute, char* raw_value) { return 404; }
  int CommandHostTiny::callfunc(char* funcname, char* raw_args) { return 404; }
  int CommandHostTiny::do_command(char* funcname) { return 404; }

  char * CommandHostTiny::consume_token(char * command_line) {
    // Modifies the buffer in place - replacing spaces with nulls each time it's called.
    // This turns out to be a very safe strategy for what we need
    char * string_boundary = strstr(command_line, " ");
    *string_boundary = 0; // Terminate the string instead of a space.
    string_boundary++;   // Move to next string
    return string_boundary;
  }

  bool CommandHostTiny::has_builtinhelp(char * name) {
    if (strcmp(name,"ping")==0) return true;
    if (strcmp(name,"devinfo")==0) return true;
    if (strcmp(name,"funcs")==0) return true;
    if (strcmp(name,"attrs")==0) return true;
    if (strcmp(name,"set")==0) return true;
    if (strcmp(name,"get")==0) return true;
    if (strcmp(name,"help")==0) return true;
    return false;
  }
  const char * CommandHostTiny::builtinhelp(char * name) {
    if (strcmp(name,"ping")==0) return "ping -> pong:str - API test function";
    if (strcmp(name,"devinfo")==0) return "devinfo -> devname:str - return information about the device.";
    if (strcmp(name,"funcs")==0) return "funcs -> funclist:str* - Return a list of function names";
    if (strcmp(name,"attrs")==0) return "attrs -> attrlist:str* - Return a list of attributes";
    if (strcmp(name,"set")==0) return "set name:str value:T - set an attribute to a value";
    if (strcmp(name,"get")==0) return "get name:str -> value:T - return an attribute's value";
    if (strcmp(name,"help")==0) return "help name:str -> helptext:str - return help for a name NB: All names are case sensitive";
    return "-";
  }



//Serial.print("ping,funcs,attrs,set,get,help");

  void CommandHostTiny::buffer_serial() {
    while (Serial.available() >0) {
      char next_char = Serial.read();
      if (line_length <140) {
        if (next_char !='\n') {
          serial_buffer[line_length] = next_char;
          serial_buffer[line_length+1] = 0; // Ensure null termination
          line_length = line_length + 1;
        } 
        else {
          have_line = true;
          return;
        }
      }
    }
    have_line = false;
  }

  void CommandHostTiny::interpret_line() {
    char command_line[140];
    if (!have_line) { return; }

    strcpy(command_line,serial_buffer); // Copy and empty serial buffer - guaranteed null terminated
    serial_buffer[0] = 0;
    line_length = 0;                    // Empty serial buffer
    have_line = false;

    if (strcmp(command_line,"ping") == 0) {
          Serial.println(F("200:OK:pong"));
        return;
    }
    if (strcmp(command_line,"attrs") == 0) {
        const char *result = attrs();
        Serial.print(F("200:ATTRS OK:"));
        Serial.print(result);
        Serial.println();
        return;
    }
    if (strcmp(command_line,"funcs") == 0) {
      const char *result = funcs();
      Serial.print(F("200:FUNCS OK:ping,devinfo,funcs,attrs,set,get,help"));
      if (strlen(result) >0) {
        Serial.print(F(","));
        Serial.print(result);
        Serial.println();
      }
      else{
        Serial.println();
      }
      return;
    }
    if (strcmp(command_line,"help") == 0) {
      Serial.println(F("200:Help found:help -> helptext:str - try 'help help', 'funcs' and 'attrs'"));
      return;
    }
    if (strcmp(command_line,"devinfo") == 0) {
      Serial.print(F("200:DEV READY:"));
      Serial.println( hostid()); // Name of the device. May or may note be used on the network verbatim
      return;
    }
    // If we find a space, it's reasonable to assume the following...
    if (strstr(command_line," ")) { // Find a space
      char * command = command_line;
      char * rest = consume_token(command_line);
      char * args = rest;

      // command.toLowerCase(); // Can we do this?
      // FIXME: provide help for built-ins
      if (strcmp(command,"help") == 0) {
        if (strstr(args," ")) {
          Serial.println(F("400:Fail:Cannot handle spaces in names when getting help"));
          return;
        }
        if (has_builtinhelp(args)) {
          const char * value = builtinhelp(args);
          Serial.print(F("200:Help found:"));
          Serial.println(value);
        }
        else if (has_help(args)) {
          Serial.print(F("200:Help found:"));
          help(args); // Prints the help - maybe not the best option. Best for the moment.
        }
        else {
          Serial.print(F("404:No help found:"));
          Serial.println(args);
        }
        return;
      }

      if (strcmp(command,"get") == 0) {
        if (strstr(args," ")) {
          Serial.println(F("400:Fail:Should not have spaces in get command"));
          return;
        }
        if (exists(args)) {
          const char * value = get(args);
          Serial.print(F("200:Found:"));
          Serial.println(value);
        } 
        else {
          Serial.println(F("404:Attribute Not Found:-"));
        }
        return;
      }

      if (strcmp(command,"set") == 0) {
          if (!strstr(args," ")) {
            Serial.println(F("400:Fail:set attribute must be given a value"));
            return;
          }

          char * attribute = args;
          char * value = consume_token(args);
          int result = set(attribute, value); // Intended to be overridden, must provide a way to describe failure...
          if (result == 200) {
            Serial.println(F("200:Success:-"));
            return;
          }
          if (result == 404) {
            Serial.println(F("404:Attribute Not Found:-"));
            return;
          }
          if (result == 500) {
            Serial.println(F("500:Bad Value:-"));
            return;
          }
          return;
        }

      // Unknown function type call
      // - hopefully a function call to the device's API
      result_string[0] = 0;
      int result = callfunc(command, args); // Intended to be overridden, must provide a way to describe failure...
      if (result == 200) {
        Serial.print(F("200:Success:"));
        if (strcmp(result_string,"")==0) {
            Serial.println(F("-"));
        } else {
            Serial.println(result_string);
        }
        return;
      }
      if (result == 404) {
        Serial.println(F("404:funcname Not Found:-"));
        return;
      }
      return;

    } else { // No space found. Could still be a single word command...
        result_string[0] = 0;

        int result = callfunc(command_line, NULL);
        if (result == 200) {
          Serial.print(F("200:Success:"));
          if (strcmp(result_string,"")==0) {
              Serial.println(F("-"));
          } else {
              Serial.println(result_string);
          }
          return;
        }
        if (result == 404) {
          Serial.println(F("404:funcname Not Found:-"));
          return;
        }
    }
  }

  void CommandHostTiny::run_host() {
    buffer_serial(); // Would be nice to have this with a timeout!
    // Would enable the thing to run more or less independently of the command host...
    // Mind you, max data rate is about a character per millisecond, so maybe just "nice"
    interpret_line();
  }

  void CommandHostTiny::setup() {
      Serial.begin(9600);    // Data rate should be configurable
      Serial.print(F("200:DEV READY:"));
      Serial.println( hostid()); // Name of the device. May or may note be used on the network verbatim
      // Ideally also want a sufficiently unique id here.
  }
