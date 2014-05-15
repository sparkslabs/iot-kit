#ifndef IOTOY_COMMANDHOST_TINY_H
#define IOTOY_COMMANDHOST_TINY_H

#include <Arduino.h>

class CommandHostTiny {
  bool have_line;
  int line_length;
  char serial_buffer[141];
  void send_response(int status_code, char* message, char* result);

public:
  CommandHostTiny() : have_line(false), line_length(0) {}
  ~CommandHostTiny() {}

  virtual const char *hostid();
  virtual const char *help(char * name);
  virtual const char * attrs();
  virtual const char * funcs();
  virtual bool exists(char * attribute);
  virtual bool has_help(char * name);
  bool has_builtinhelp(char * name);
  const char *builtinhelp(char * name);

  virtual const char *get(char * attribute);
  virtual int set(char* attribute, char* raw_value);
  virtual int callfunc(char* funcname, char* raw_args);
  virtual int do_command(char* funcname);

  char * consume_token(char * command_line);
  void buffer_serial();
  void interpret_line();
  void run_host();
  virtual void setup();

};

#endif