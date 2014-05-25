/*

The reason this doesn't use "make" is to avoid a clash with the way this directory is
intended to be used. Yes, it's suboptimal, but it's intended to bootstrap a decent
testing process, and will probably disappear at some point. (famous last words)

Currently testing like this:

./stdio_host_test.sh 2>run_log.txt && cat run_log.txt


*/

#include <iostream>
#include <Arduino.h>

// These four for unbuffered stdin IO (hmm, wonder if that breaks stdout?)
#include <stdio.h>
#include <sys/select.h>
#include <unistd.h>
#include <termios.h>

#include <string>
#include <sstream>

#ifdef TESTING

#include <CommandHostTiny.h>

// Minimal Host for testing with
class TestHost : public CommandHostTiny {
public:
  TestHost() { }
  ~TestHost() { }

  const char *hostid() { 
    std::cerr << "TestHost::hostid()" << std::endl;
    return "stdiotest";
  }
  void setup(void) {
      // Setup the pins
      std::cerr << "TestHost::setup()" << std::endl;
       CommandHostTiny::setup();
  }
};

TestHost MyCommandHost;

void setup() {
   std::cerr << "setup()" << std::endl;
   MyCommandHost.setup();
}

void loop() {
//    std::cerr << "loop()" << std::endl;
   MyCommandHost.run_host();
}

#else

// NOTE: %INOFILE% needs to be replaced before building, or else
// build will fail. Example makefiles handle this sort of thing
// already
#include "%INOFILE%"
#endif

#define STDIN 0

bool stdin_available() {
  struct timeval timeout;
  usleep(10); // Don't burn CPU
  fd_set fds;
  timeout.tv_sec = 0;
  timeout.tv_usec = 1000;
  FD_ZERO(&fds);
  FD_SET(STDIN, &fds);
  select(STDIN+1, &fds, NULL, NULL, &timeout);
  return FD_ISSET(STDIN, &fds);
}

int main(int argc, char *argv[]) {
  std::string line;
 DEBUG_OFF;
    Serial.reset();
    Serial.dump();

     setup();
     while (!Serial._shutdown_signalled()) { // The StdioSerial module has this additional function - to allow us to shut the system down.
       loop();
        if (stdin_available()) {
           std::getline(std::cin, line);
           Serial.send_from_host(line+"\n");
        }
        if (std::cin.eof()) {
          break;
        }

        try {
          std::string result = Serial.recv_on_host();
          std::cout << result;
        } catch (...) { }
     }
  return 0;
}
