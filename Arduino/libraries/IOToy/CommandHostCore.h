#ifndef IOTOY_COMMANDHOST_CORE_H
#define IOTOY_COMMANDHOST_CORE_H

#include <Arduino.h>

class CommandHost {
// Provides the basics of a command host for the user to override all the interesting bits of.
// Handles all the boring details.
  int line_length;
  bool have_line;
  String serial_buffer;

public:

  CommandHost() : have_line(false), line_length(0), serial_buffer("") {}
  ~CommandHost() {}
  void _ping();
  void _attrs();
  void _funcs();
  void _help();
  void _help(String name);
  void _get(String attribute);
  void _set(String set_spec);
  // Domain Specific Function - should be overridden really
  virtual String help(String name);
  virtual String attrs();
  virtual String funcs();
  virtual bool exists(String attribute);
  virtual bool has_help(String name);
  virtual String get(String attribute);
  virtual int set(String attribute, String raw_value);

  void interpret_line();
  void buffer_serial();
  void run_host();

};

#endif
