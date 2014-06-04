# Web API

Document version: 1.0-alpha

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

## Directory values

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

### Future expansion

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

## GET Representations

The GET representation of each of these, follows the following form:

    { "type" : "iotoyt.org/types/TYPE",
      "href" : "/some_flag",
      "help" : "Human friendly help text",
      "value" : REPRESENTATION }

The representation for each is relative obvious, except for callables (functions)
and Exceptions.

### Value representation

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

### Example bool representation

    {
      "type" : "iotoy.org/types/bool",
      "href" : "/some_flag",
      "help" : "This represents a flag.",
      "value" : true
    }

### Example int representation

    {
      "type" : "iotoy.org/types/int",
      "href" : "/some_counter",
      "help" : "This represents a counter.",
      "value" : 10
    }

### Sample  float representation

    {
      "type" : "iotoy.org/types/float",
      "href" : "/some_ratio",
      "help" : "This represents a ratio.",
      "value" : 3.1459
    }

### Sample  string representation

    {
      "type" : "iotoy.org/types/str",
      "href" : "/some_name",
      "help" : "This represents some string, perhaps a name.",
      "value" : "Frank"
    }

### Sample  json representation

    {
      "type" : "iotoy.org/types/json",
      "href" : "/some_structure" ,
      "help" : "This represents some structure.",
      "value" : { "this" : ["is", "any", "valid"],
                  "json" : "object" }
    }

### Representation of functions

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

### Sample Exception representation

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

## PUT Representations / Behaviour

Put will generally use the same format as GET representations

  * Client - will consist of PUTing a value to the site - at present this is the bare value, but
    it should really be a resource
  * Site - will consist of returning the GET value for the attribute or an exception

## POST Representations / Behaviour

POST representations have two halves:

  * Client - currently this consists of sending a bare value as the body of the POST request
  * Site - the response is a json value broadly matching that from a GET request, without the
    provision of an href. Additionally there is an extra return type of "None" (aka null)

