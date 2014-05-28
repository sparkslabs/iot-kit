## Running stack of cards completed

* Auto-webAPI allows calling of functions with no arguments.
* Automated Web API allows getting / setting of device proxy attributes
* Move introspection code into python install area
* Make python code dev loop deb package based
* Device Proxy is autogenerated for stdio device
* Python API allows function calls with a return argument to a stdio device
* Python API allows function calls with 1 arg to a stdio device
* Python API allows basic function calls to a stdio device
* Python API presents something looking like a function to the user for a stdio device
* get/set python attribute gets/sets device attribute for stdio device
* Python spike for introspecting a device exists
* Test Host covers all useful introspection cases
* Test Host exists for testing API introspection
* Python subprocess access to an stdio iotoy host works properly
* It is possible to set the argument to the empty string as per spec
* C-API is introspectable
* BUGFIX: devinfo missing from funcs/help
* BUGFIX: funcspec for help, funcs and attrs misses off result name
* Serial API has draft docs
* C API 'command' support needs consistency
* BUGFIX: help in BotHostTiny was inconsistent
* BUGFIX: Calling "set" with no/missing value causes crash
* C API should mock serial IO via stdin/stdout
* BUGFIX: Fix host's resilience against being sent junk
* Initial Stdio Mock Serial exists, allowing fleshing out of core
* Mock build environment for C API is reinstated
* arduino-iotoy can be built/tested without the UI
* Break python spike up into first cut of modules
* Installation of arduino-iotoy for non-ubuntu hosts 
* Debian packaging for iotoy-libs
* Iotoy python installs in standard places
* Debian packaging for iotoy python
* Scratch implementation of the oven api exsts
* Github repository exists
* Arduino command host code exists
* Scratch API is completed and documented