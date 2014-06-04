Serial Communications Protocol
==============================

Current: May 2014

All messages have the form:

    <status code>:<Human readable status>:<data>

Below --> means "sent to device", <-- means "received from device".

 * Status code - a numerical value, based on HTTP status codes
 * Human readable status - can be passed through to people
 * data - intended to be parsed by machines

Switch on:

    --> (nothing sent)
    <-- 200:DEV READY:<device id>

Device id may be one of the two following options:

 * plainid
 * plainid ":" specifierid

The plainid *must* be something that can be used in DNS. A good rule of thumb
for this is that it should match the following regex: [a-zA-Z][a-zA-Z0-9_]*

The specifier id, if used, must also be something that can be used in DNS, and it
should conform to the regex [a-zA-Z][a-zA-Z0-9_]*

The idea is that the plainid is generally expected to refer to a class of devices,
and the specifier id would refer to a specific device.

Base function:

    --> help
    <-- found:help -> str - try 'help help', 'funcs' and 'attrs

This enables discovery of functions:

    --> funcs
    <-- 200:FUNCS OK:ping,funcs,attrs,set,get,help,devinfo

For the BotHostTiny this looks like this:

    --> funcs
    <-- 200:FUNCS  OK:ping,funcs,attrs,set,get,help,forward,backward,left,right,on,off

Data format is a list of tokens. 

General form:
    --> funcs
    <-- 200:FUNCS  OK:<func list>

Where funclist is a comma separated list of names of the form [a-z][a-z0-9_]* with
no spaces. NB: No capitals.

Discovery of attributes:

    --> attrs
    <-- 200:ATTRS OK:drive_forward_time_ms:int,turn_time_ms:int

General form:
    --> attrs
    <-- 200:FUNCS  OK:<attrlist>

Where attrlist is a comma separated list of <attrspec>. Each attrspec has the following
form:

    attrname ":" attrtype

Note:

 * attrname is of the form [a-z][a-z0-9_]* with no spaces. NB: No capitals.
 * attrtype must be one of "str" "int" "float" or "bool"
   * No support for structure at present. Some variant of binary json will be specified
     however at some point after an evaluation of various options has taken place.
   * IFF style data chunking is a valid alternative for structure.

Note the data format here is a list of tokens and types. Valid types - interms of current implementations are str and int initially - may expand to basic json types.

This allows the extraction of attributes and checks that the values passed down to the C API are of the right type.

In order to allow devices to be self documenting, help can be provided for attributes:

    --> help drive_forward_time_ms
    <-- 200:Help found:int - How long to move forward

    --> help turn_time_ms
    <-- 200:Help found:int - How long to turn

Note the data format here is:

    <type> " - " <description>

Similary, help for functions is there to aid introspection and self documentation. The
general form is this:

    --> help <funcname>
    <-- 200:Help found:<funcname> <funcspec> - Description

Where:

 * funcname is of the form [a-z][a-z0-9_]*
 * funcspec has the form:

     <argspec> " -> " <resultspec>

 * argspec may be empty
 * result spec may be empty
 * If argspec is not empty it has the form:  <name> ":" <type>
 * If resultspec is not empty, it has the form <name> ":" <type>
 * name - must be [a-z][a-z0-9_]*
 * type describes the type of the argument/result and may be the following:
    - str - string - no quotes should be used
        - This seems awkward, but remember this would set a string to empty:
          - "set name \n"
          As opposed to non-empty:
          - "set name .\n"
          You can't have an empty attribute or function name.

    - int - may be up to +-2**31. If you need more, use more attributes
    - float - IEEE 754 double
    - bool - valid representations of true: 1, true, True, t, T
           - valid representations of false: 0, false, False, f, F
    - T -- This is a special case meaning the type will vary. This sounds mad, until
           you realise that this is helps define "get" and "set" where the return or
           argument type depends on the attribute.

The upshot of this is that the following are valid responses for attributes and functions:
    "200:Help found:int - How long to move forward"
    "200:Help found:int - How long to turn"
    "200:Help found:forward dist:int -> - Move forward for a distance"
    "200:Help found:backward dist:int -> - Move backward for a distance"
    "200:Help found:on -> - Turn on"
    "200:Help found:off -> - Turn off"
    "200:Help found:set name:str value:T -> - set an attribute to a value"
    "200:Help found:get name:str -> value:T - return an attribute's value"

It should be relatively clear here that:

* on/off map to functions without any arguments and no result
* forward/backward map to functions with 1 argument and no result
* get maps to a function with 1 argument and a result
* set maps to a function with 2 arguments and no result - this is currently a special
  case and not generally supported
* The lack of "->" in the first two indicate they are response strings from attributes
  not functions - which means they only mention the type and human readable text.
