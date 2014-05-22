Example walkthrough the Serial API using BotHostTiny
====================================================

start:

    send: (device start up)
    recv: "200:DEV READY:sumobot"

standard introspection:

    send: "help"
    recv: "found:help -> str - try 'help help', 'funcs' and 'attrs'"

    send: "help help"
    recv: "200:Help found:help name:str -> str - return help for a name NB: All names are case sensitive"

    send: "help funcs"
    recv: "200:Help found:funcs -> str* - Return a list of function names"

    send: "help attrs"
    recv: "200:Help found:attrs -> str* - Return a list of attributes"

    send: "help set"
    recv: "200:Help found:set name:str value:T -> - set an attribute to a value"

    send: "help get"
    recv: "200:Help found:get name:str -> value:T - return an attribute's value"

BotHostTiny introspection:

    send: "help forward"
    recv: "200:Help found:forward -> - Move forward for drive_forward_time_ms milliseconds"

    send: "help backward"
    recv: "200:Help found:backward -> - Move backward for drive_forward_time_ms milliseconds"

    send: "help left"
    recv: "200:Help found:left -> - Turn left for turn_time_ms milliseconds"

    send: "help right"
    recv: "200:Help found:right -> - Turn right for turn_time_ms milliseconds"

    send: "help on"
    recv: "200:Help found:on -> - Turn on"

    send: "help off"
    recv: "200:Help found:off -> - Turn off"

    send: "help drive_forward_time_ms"
    recv: "200:Help found:int - How long to move forward"

    send: "help turn_time_ms"
    recv: "200:Help found:int - How long to turn"

standard functions:

    send: "devinfo"
    recv: "200:DEV READY:sumobot"

    send: "ping"
    recv: "200:OK:pong"

    send: "funcs"
    recv: "200:FUNCS OK:ping,funcs,attrs,set,get,help,forward,backward,left,right,on,off"

    send: "attrs"
    recv: "200:ATTRS OK:drive_forward_time_ms:int,turn_time_ms:int"

Access (discovered) BotHostTiny attributes:

    send: "get drive_forward_time_ms"
    recv: "200:Found:1500"

    send: "get turn_time_ms"
    recv: "200:Found:2000"

    send: "set drive_forward_time_ms"
    recv: "400:Fail:set attribute must be given a value"

    send: "set turn_time_ms"
    recv: "400:Fail:set attribute must be given a value"

    send: "set drive_forward_time_ms 2000"
    recv: "200:Success:-"

    send: "set turn_time_ms 1000"
    recv: "200:Success:-"

    send: "get drive_forward_time_ms"
    recv: "200:Found:2000"

    send: "get turn_time_ms"
    recv: "200:Found:1000"

Use (discovered) BotHostTiny functions:

    send: "forward"
    recv: "200:Success:-"

    send: "backward"
    recv: "200:Success:-"

    send: "left"
    recv: "200:Success:-"

    send: "right"
    recv: "200:Success:-"

    send: "off"
    recv: "404:funcname Not Found:-"

    send: "on"
    recv: "404:funcname Not Found:-"
