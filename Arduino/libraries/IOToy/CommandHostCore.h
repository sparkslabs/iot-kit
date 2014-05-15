#ifndef IOTOY_COMMANDHOST_CORE_H
#define IOTOY_COMMANDHOST_CORE_H

#include <Arduino.h>

class CommandHost {
  // @module IOToy.CommandHost
  // Files: CommandHost.cpp / CommandHost.h
  //
  // Provides the core functionality of the system for your typical arduino platform.
  //
  // @class CommandHost
  // This provides a basic command host for your arduino device. For devices using a smaller
  // arduino (eg based on an Atmel 8A or similar), you probably want to use the CommandHostTiny
  // class instead.
  //
  // It provides a base class for you to subclass. The base class provides the following
  // core functionality
  //
  // * It provides a hook for your run loop to poll the serial connection for commands
  //   and a means of interpreting these commands, and sending back responses over the
  //   serial connection to the user of the device
  // * It provides the following default commands to a user of the device:
  // ** ping - responds with "pong"
  // ** attrs - calls an attrs() function, and sends the result to the user.
  // ** funcs - calls a funcs() function, and sends the result along with the default functions
  // ** help - provides a hook for help functionality - both builtin and device specific
  // ** set - used for setting an attribute value
  // ** get - used for getting an attribute value
  //

  bool have_line;
  int line_length;
  String serial_buffer;

public:

  CommandHost() : have_line(false), line_length(0), serial_buffer("") {}
  // @func CommandHost::CommandHost()
  // Constructor, no arguments
  //

  ~CommandHost() {}
  //@func CommandHost::~CommandHost()
  // destructor, no arguments
  //

  void _ping();
  //@func CommandHost::_ping()
  // Called by CommandHost::interpret_line()
  //
  // Sends "pong" back to the user of the device. Basic health check.
  //

  void _attrs();
  //@func CommandHost::_ping()
  // Called by CommandHost::interpret_line()
  // Calls attrs() - expected to be implemented in subclass (see @@attrs() )
  //
  //
  // The result is expect to be a 
  // 
  // Sends "pong" back to the user of the device. Basic health check.

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
