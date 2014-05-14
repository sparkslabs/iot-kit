
#include <iostream>
#include <string.h>
#include <stdlib.h>

#define LOCALTEST 1

#include <Arduino.h>
#include <ctype.h>


void DEBUG_dumpstring(String thestring, std::string pretext) {
      unsigned int size = thestring.length()+1;
      unsigned char * bytes = (unsigned char *) malloc(size);
      thestring.getBytes(bytes, size);
      std::cout << "DEBUG: " << pretext << ">>" << bytes << "<<" << std::endl;
      free(bytes);
}

void DEBUG_dumpstring(String thestring) {
  DEBUG_dumpstring(thestring, "");
}

#include "%INOFILE%"

bool test_buffering_in_serial_interface = false;
bool test_basic_commands = false;
bool test_get = true;
bool test_set = false;
bool test_help = false;

/* Useful code */

int main(int argc, char* argv[]) {
    /* Purpose of this main loop is to run the setup and loop functions and to
     * inject values into the mock serial interface, allowing exercising of the loop */
// DEBUG_ON ;
// Test the core functionality
    setup();
// ------------------------
// Test the buffering in the serial interface
    if (test_buffering_in_serial_interface) {
        Serial.send_from_host("fu");
        loop();
        Serial.send_from_host("n");
        loop();
        loop();
        loop();
        loop();
        Serial.send_from_host("cs\natt");
        loop();
        Serial.send_from_host("rs\nping\n");
        loop();
    }

    // Test basic commands
    if (test_basic_commands) {
        Serial.send_from_host("ping\n");
        loop();
        Serial.send_from_host("attrs\n");
        loop();
        Serial.send_from_host("funcs\n");
        loop();
        Serial.send_from_host("help\n");
        loop();
        Serial.send_from_host("pong\n");
        loop();
    }

    if (test_get) {
        // TEST GET
        Serial.send_from_host("get temperature\n");
        loop();
        std::cout << "------ ITER ------" << std::endl;
        Serial.send_from_host("get target_temperature\n");
        loop();
        std::cout << "------ ITER ------" << std::endl;
        Serial.send_from_host("get flibble\n");
        loop();
        std::cout << "------ ITER ------" << std::endl;
    }

    // TEST SET

    if (test_set) {
        Serial.send_from_host("set temperature 10\n");
        loop();
        Serial.send_from_host("set target_temperature 10\n");
        loop();
        Serial.send_from_host("set non_existent 10\n");
        loop();
    }
    // TEST HELP COMMANDS
    if (test_help) {
        Serial.send_from_host("help temperature\n");
        loop();
        Serial.send_from_host("help target_temperature\n");
        loop();
        Serial.send_from_host("help on\n");
        loop();
        Serial.send_from_host("help off\n");
        loop();
        Serial.send_from_host("help set\n");
        loop();
        Serial.send_from_host("help get\n");
        loop();
    }
}

