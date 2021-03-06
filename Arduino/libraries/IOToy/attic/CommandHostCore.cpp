#include <CommandHostCore.h>
#include <Arduino.h>

void CommandHost:: _ping() {
    Serial.println("pong");
}

void CommandHost::_attrs() {
    String result = attrs();

    unsigned int size = result.length()+1;
    unsigned char * bytes = (unsigned char *) malloc(size);
    result.getBytes(bytes, size);
    Serial.println((const char*)bytes);
    free(bytes);
}

void CommandHost::_funcs() {
    String result = funcs();
    Serial.print("ping,funcs,attrs,set,get,help");
    if (result.length() >0) {
        unsigned int size = result.length()+1;
        unsigned char * bytes = (unsigned char *) malloc(size);
        result.getBytes(bytes, size);
        Serial.print(",");
        Serial.println((const char*)bytes);
        free(bytes);
    } else{
        Serial.println("");
    }
}

void CommandHost::_help() {
    Serial.println("help - provides this help. help $symbol - provides help on the given symbol, if it exists");
}

void CommandHost::_help(String name) {
    if (name.indexOf(" ") != -1 ) {
        Serial.println("400:Fail:Cannot handle spaces in names when getting help");
        return;
    }
    if (has_help(name)) {
        String value = help(name);
        Serial.print("200:Help Found:");

        unsigned int size = value.length()+1;
        unsigned char * bytes = (unsigned char *) malloc(size);
        value.getBytes(bytes, size);
        Serial.println((const char*)bytes);
        free(bytes);
    } else {
        Serial.println("404:No help Found:-");
    }
}

void CommandHost::_get(String attribute) {
    if (attribute.indexOf(" ") != -1 ) {
        Serial.println("400:Fail:Should not have spaces in get command");
        return;
    }
    if (exists(attribute)) {
        String value = get(attribute);
        Serial.print("200:Found:");

        unsigned int size = value.length()+1;
        unsigned char * bytes = (unsigned char *) malloc(size);
        value.getBytes(bytes, size);
        Serial.println((const char*)bytes);
        free(bytes);

    } else {
        Serial.println("404:Attribute Not Found:-");
    }
}

void CommandHost::_set(String set_spec) {
    if (set_spec.indexOf(" ") != -1 ) {
        String attribute = set_spec.substring(0, set_spec.indexOf(" "));
        String value = set_spec.substring(set_spec.indexOf(" ")+1);
        int result = set(attribute, value); // Intended to be overridden, must provide a way to describe failure...

        if (result == 200) {
            Serial.println("200:Success:-");
            return;
        }
        if (result == 404) {
            Serial.println("404:Attribute Not Found:-");
            return;
        }
    } else {
        Serial.println("400:Fail:Must provide an argument...");
    }
}
  
// Domain Specific Function - should be overridden really
String CommandHost::help(String name) { return String(""); }
String CommandHost::attrs() { return String(""); }
String CommandHost::funcs() { return String(""); }
bool CommandHost::exists(String attribute) { return false; }
bool CommandHost::has_help(String name) { return false; }
String CommandHost::get(String attribute) { return String("-"); }
int CommandHost::set(String attribute, String raw_value) { return 404; }

void CommandHost::interpret_line() {
  if (!have_line) { return; }
     String command_line = serial_buffer;
      serial_buffer = "";
      have_line = false;

      // Check core non-spaced functions first
      if (command_line == "ping") { // Basic liveness test
        _ping();
        return;
      }
      if (command_line == "attrs") {
        _attrs();
        return;
      }
      if (command_line == "funcs") {
        _funcs();
        return;
      }
      if (command_line == "help") {
        _help();
        return;
      }
      if (command_line.indexOf(" ") != -1 ) {
        String command = command_line.substring(0, command_line.indexOf(" "));
        String args = command_line.substring(command_line.indexOf(" ")+1);
        command.toLowerCase();
        if (command == "set") {
          _set(args);
          return;
        }
        if (command == "get") {
          _get(args);
          return;
        }
        if (command == "help") {
          _help(args);
          return;
        }
      }

      // Something else
}

void CommandHost::buffer_serial() {
    while (Serial.available()) {
      char next_char = Serial.read();
      if (line_length <140) {
        if (next_char !='\n') {
          serial_buffer = serial_buffer + next_char;
        } else {
          have_line = true;
          return;
        }
      }
    }
    have_line = false;
}

void CommandHost::run_host() {
    buffer_serial(); // Would be nice to have this with a timeout!
                     // Would enable the thing to run more or less independently of the command host...
                     // Mind you, max data rate is about a character per millisecond, so maybe just "nice"
    interpret_line();
}
