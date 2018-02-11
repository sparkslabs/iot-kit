---
template: mainpage
source_form: markdown
name: IOTOY Specifications
updated: Feb 2018
title: IOTOY Specifications
---

## IOTOY Specifications

**Internet Of Things Of Yours** specifications are divided into the following two main areas:

* **Serial API** - This is a seria communications protocl, loosely based on
  ideas from HTTP, but aimed at being simple enough for very small devices
  to implement.

* **Web API** - A pure REST based interface. It is built entirely automatically
  from the Serial API, and provides enough information for a python proxy
  object to be created on a client machine.


### Core Concepts

The core concepts are:

* Device introspection - I want to pick up this device and as it how it works?
* Device as software - Using that introspection, can I automatically create a linguistic interface suitable for use in my language? The example language is python
* Network introspection - can I find the device, connect to it and ask it how it works?
* Network Device as software - Using that introspection, can I automatically create a linguistic interface suitable for use in my language? Again, using python

There are some basic standard types available - that map to the types
you find in many languages. Additionally a type for functions and
exceptions exists.

These types are defined within the iotoy.org/types namespace - a couple
of examples: iotoy.org/types/int, iotoy.org/types/function

(These types actually refer to real URLs that resolve, and give both
human and machine readable versions dependent on HTTP header provided)

However, an industry may choose to define their own types, and these
can sit within their namespace. For example iot-kit/types/servo


### Serial API - Serial Communications Protocol

Last Update: May 2014
Status: Stable

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

### Web API

Status: 1.0

The web API provides a linguistic mapping of HTTP methods to a traditional programming languages.
Python is the default language but the principles apply to many languages.

Key points:

* Web servers are objects
* Resources are attributes
* HTTP GET maps to \_\_getattribute\_\_ on the web server object for a given attribute
* HTTP PUT maps to \_\_setattr\_\_ on the web server object for a given attribute
* HTTP POST maps to \_\_call\_\_ on the web server object for a given attribute

What is transfered by an HTTP GET? A representation of the attribute of the web server object.
For this to map to a valid python type we need to constrain the values that will be represented.
The following types are valid:

* bool
* int
* float
* string
* callable (function)
* exception

Is IS likely that a further basic datatype - JSON - will be added at a later point in time.

Resources themselves use JSON as the transfer and representation format.

#### Directory values

In most webservers, "/" at the end of an URL has a special meaning. For example
http://iotoy.org/types/ would be expected to be a directory listing of what is
inside the value "types". The same holds for iotoy objects.

For the moment the key usecase is to find out what is inside a device.

For example:

    http://some_device_ip:port/

Is actually asking for the "/" resource on the device. As a result it returns a
directory listing object that looks like this:

    {'type': 'dir',
     'href' : '/',
     'help' : 'test_host',
     'value': ['barecommand',
               'one_arg_T',
               'no_arg_result_int',
               'no_arg_result_bool',
               'no_arg_result_T',
               'one_arg_int_result_int',
               'no_arg_result_str',
               'one_arg_int',
               'one_arg_bool',
               'no_arg_result_float',
               'one_arg_str',
               'one_arg_float',
               'str_id',
               'turn_time_ms',
               'drive_forward_time_ms',
               'some_flag',
               'ratio',
               'devinfo']}

Much like if these were "normal" hrefs, these get evaluated within the context "/", so
"barecommand" in the content "/" evaluates as "/barecommand"

#### Future expansion

The idea here is for this to allow future expansion for composite objects that might
look like this:

http://some_device_ip:port/ containing:

    {'type': 'dir',
     'href' : '/',
     'help' : 'robo cat',
     'value': ['front_left_leg',
               'front_right_leg',
               'back_left_leg',
               'back_right_leg',
               'devinfo']}

And then http://some_device_ip:port/front_left_leg containing:

    {'type': 'dir',
     'href' : '/front_left_leg/',
     'help' : 'robo cat',
     'value': ['lift',
               'lower',
               'speed',
               'claws',
               'devinfo']}

And so on.

#### GET Representations

The GET representation of each of these, follows the following form:

    { "type" : "iotoyt.org/types/TYPE",
      "href" : "/some_flag",
      "help" : "Human friendly help text",
      "value" : REPRESENTATION }

The representation for each is relative obvious, except for callables (functions)
and Exceptions.

#### Value representation

The top level attributes in a value are used for storing attributes about the value
being represented. They should be treated (generally) as immutable. The actual value
is inside a "value" field.

The default top level attributes are:

* __type__ -- The value type, which references it's definition - eg iotoy.org/types/int
* __href__ -- The location the value was retrived from.
 * Maybe a bad idea. Maybe __name__ would be better
* __help__ -- Any help test associated with this value
* __value__ -- The actual value (or rather its representation).

Addition top level attributes are:

* __methods__ -- list of valid methods for the attribute
* __constraints__ -- some representation of constraints for the values. Specifics TBD.

#### Example bool representation

    {
      "type" : "iotoy.org/types/bool",
      "href" : "/some_flag",
      "help" : "This represents a flag.",
      "value" : true
    }

#### Example int representation

    {
      "type" : "iotoy.org/types/int",
      "href" : "/some_counter",
      "help" : "This represents a counter.",
      "value" : 10
    }

#### Sample  float representation

    {
      "type" : "iotoy.org/types/float",
      "href" : "/some_ratio",
      "help" : "This represents a ratio.",
      "value" : 3.1459
    }

#### Sample  string representation

    {
      "type" : "iotoy.org/types/str",
      "href" : "/some_name",
      "help" : "This represents some string, perhaps a name.",
      "value" : "Frank"
    }

#### Sample  json representation

    {
      "type" : "iotoy.org/types/json",
      "href" : "/some_structure" ,
      "help" : "This represents some structure.",
      "value" : { "this" : ["is", "any", "valid"],
                  "json" : "object" }
    }

#### Representation of functions

Note that the purpose here is to allow introspection by machines and people. As a
result it has a calling spec, help and a name. The name generally matches the URL
stem (in this case "/some_function")

NOTE that the qualification of types is optional here - int/bool/float/string are all
assumed to be qualified as being from the iotoy.org/types/ namespace

    {
      "type" : "iotoy.org/types/function",
      "href" : "/some_function",
      "help": "test, one arg, one result, both ints",
      "value" : {
                  "name": "some_function",
                  "spec": {
                            "args": [
                                      [ "myarg","int" ]
                                    ],
                            "result": [
                                        [ "result", "int" ]
                                      ]
                          }
                }
    }

#### Sample Exception representation

    {
      "type" : "iotoy.org/types/str",
      "href" : "/some_name" ,
      "help" : "This exception generally means...",
      "value" :  { Format here is to be decided, and a work in progress.
                   The idea is to pass back any python error to the calling
                   code in a machine parsable way, so that when things go
                   wrong, you can fix them.
                 }
    }

#### PUT Representations / Behaviour

Put will generally use the same format as GET representations

  * Client - will consist of PUTing a value to the site - at present this is the bare value, but
    it should really be a resource
  * Site - will consist of returning the GET value for the attribute or an exception

#### POST Representations / Behaviour

POST representations have two halves:

  * Client - currently this consists of sending a bare value as the body of the POST request
  * Site - the response is a json value broadly matching that from a GET request, without the
    provision of an href. Additionally there is an extra return type of "None" (aka null)


