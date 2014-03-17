// Source code library, to enable clear split between user code and application code.

#ifndef IOTOY_COMMANDHOST_TINY_CPP
#define IOTOY_COMMANDHOST_TINY_CPP

// The serial lines commented out below are commented out primarily because they
// have been found to use more memory that their alternatives.

class CommandHost {
  int line_length;
  bool have_line;
  char serial_buffer[141];
  void send_response(int status_code, char* message, char* result) {
      Serial.print(status_code);
      Serial.print(":");
      Serial.print(message);
      Serial.print(":");
      Serial.print(result);
      Serial.println();
  }

public:
  CommandHost() : have_line(false), line_length(0) {}
  ~CommandHost() {}

  virtual const char *help(char * name) { return ""; }
  virtual const char * attrs() { return ""; }
  virtual const char * funcs() { return ""; }
  virtual bool exists(char * attribute) { return false; }
  virtual bool has_help(char * name) { Serial.println("Bollocks"); Serial.println(name); Serial.println("Balls");return false; }
  virtual const char *get(char * attribute) { return "-"; }
  virtual int set(char* attribute, char* raw_value) { return 404; }

  char * consume_token(char * command_line) {
    // Modifies the buffer in place - replacing spaces with nulls each time it's called.
    // This turns out to be a very safe strategy for what we need
    char * string_boundary = strstr(command_line, " ");
    *string_boundary = 0; // Terminate the string instead of a space.
    string_boundary++;   // Move to next string
    return string_boundary;
  }

  void buffer_serial() {
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

  void interpret_line() {
    char command_line[140];
    if (!have_line) { return; }

    strcpy(command_line,serial_buffer); // Copy and empty serial buffer - guaranteed null terminated
    serial_buffer[0] = 0;
    line_length = 0;                    // Empty serial buffer
    have_line = false;

    if (strcmp(command_line,"ping") == 0) {
        send_response(200, (char*) "OK", (char*) "pong");
//          Serial.println("200:OK:pong");
        return;
    }
    if (strcmp(command_line,"attrs") == 0) {
        const char *result = attrs();
        Serial.print(result);
        Serial.println();
        return;
    }
    if (strcmp(command_line,"funcs") == 0) {
      const char *result = funcs();
      Serial.print("ping,funcs,attrs,set,get,help");
      if (strlen(result) >0) {
        Serial.print(",");
        Serial.print(result);
        Serial.println();
      } else{
        Serial.println();
      }
      return;
    }
    if (strcmp(command_line,"help") == 0) {
      Serial.println(F("help - try 'help help', 'funcs' and 'attrs'"));
      return;
    }
    if (strstr(command_line," ")) { // Find a space
      char * command = command_line;
      char * rest = consume_token(command_line);
      char * args = rest;

      // command.toLowerCase(); // Can we do this?
      if (strcmp(command,"help") == 0) {
        if (strstr(args," ")) {
          Serial.println(F("400:Fail:Cannot handle spaces in names when getting help"));
          return;
        }
        if (has_help(args)) {
          const char * value = help(args);
          Serial.print(F("200:Help found:"));
          Serial.println(value);
        } else {
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
          send_response(200, (char*)"Found", (char*)value);
//          Serial.print("200:Found:");
//          Serial.println(value);
        } else {
          Serial.println("404:Attribute Not Found:-");
        }
        return;
      }

      if (strcmp(command,"set") == 0) {
          char * attribute = args;
          char * value = consume_token(args);
          Serial.print("Attribute:");
          Serial.println(attribute);
          Serial.print("Value:");
          Serial.println(value);
          int result = set(attribute, value); // Intended to be overridden, must provide a way to describe failure...
          if (result == 200) {
            Serial.println("200:Success:-");
            return;
          }
          if (result == 404) {
            Serial.println("404:Attribute Not Found:-");
            return;
          }
          return;
      }
    }
  }

  void run_host() {
    buffer_serial(); // Would be nice to have this with a timeout!
    // Would enable the thing to run more or less independently of the command host...
    // Mind you, max data rate is about a character per millisecond, so maybe just "nice"
    interpret_line();
  }
};

#endif
