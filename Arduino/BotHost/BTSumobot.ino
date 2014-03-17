
class CommandHost {
  int line_length;
  bool have_line;
  char serial_buffer[141];
  void send_response(int status_code, char* message, char* result) {
    Serial.print(status_code);
    Serial.print(":");
    Serial.print(message);
    Serial.print(":");
    Serial.print(result);
    Serial.println();
  }

public:
  CommandHost() : 
  have_line(false), line_length(0) {
  }
  ~CommandHost() {
  }

  virtual const char *hostid() { 
    return "generic_1";
  }
  virtual const char *help(char * name) { 
    return ""; 
  }
  virtual const char * attrs() { 
    return ""; 
  }
  virtual const char * funcs() { 
    return ""; 
  }
  virtual bool exists(char * attribute) { 
    return false; 
  }
  virtual bool has_help(char * name) { 
    Serial.println("Bollocks"); 
    Serial.println(name); 
    Serial.println("Balls");
    return false; 
  }
  virtual const char *get(char * attribute) { 
    return "-"; 
  }
  virtual int set(char* attribute, char* raw_value) { 
    return 404; 
  }
  virtual int callfunc(char* funcname, char* raw_args) { 
    return 404; 
  }

  char * consume_token(char * command_line) {
    // Modifies the buffer in place - replacing spaces with nulls each time it's called.
    // This turns out to be a very safe strategy for what we need
    char * string_boundary = strstr(command_line, " ");
    *string_boundary = 0; // Terminate the string instead of a space.
    string_boundary++;   // Move to next string
    return string_boundary;
  }

  void buffer_serial() {
    while (Serial.available() >0) {
      char next_char = Serial.read();
      if (line_length <140) {
        if (next_char !='\n') {
          serial_buffer[line_length] = next_char;
          serial_buffer[line_length+1] = 0; // Ensure null termination
          line_length = line_length + 1;
        } 
        else {
          have_line = true;
          return;
        }
      }
    }
    have_line = false;
  }

  void interpret_line() {
    char command_line[140];
    if (!have_line) { 
      return; 
    }

    strcpy(command_line,serial_buffer); // Copy and empty serial buffer - guaranteed null terminated
    serial_buffer[0] = 0;
    line_length = 0;                    // Empty serial buffer
    have_line = false;

    if (strcmp(command_line,"ping") == 0) {
      send_response(200, "OK", "pong");
      //          Serial.println("200:OK:pong");
      return;
    }
    if (strcmp(command_line,"attrs") == 0) {
      const char *result = attrs();
      Serial.print(result);
      Serial.println();
      return;
    }
    if (strcmp(command_line,"funcs") == 0) {
      const char *result = funcs();
      Serial.print("ping,funcs,attrs,set,get,help");
      if (strlen(result) >0) {
        Serial.print(",");
        Serial.print(result);
        Serial.println();
      } 
      else{
        Serial.println();
      }
      return;
    }
    if (strcmp(command_line,"help") == 0) {
      Serial.println(F("help - try 'help help', 'funcs' and 'attrs'"));
      return;
    }
    if (strstr(command_line," ")) { // Find a space
      char * command = command_line;
      char * rest = consume_token(command_line);
      char * args = rest;

      // command.toLowerCase(); // Can we do this?
      if (strcmp(command,"help") == 0) {
        if (strstr(args," ")) {
          Serial.println(F("400:Fail:Cannot handle spaces in names when getting help"));
          return;
        }
        if (has_help(args)) {
          const char * value = help(args);
          Serial.print(F("200:Help found:"));
          Serial.println(value);
        } 
        else {
          Serial.print(F("404:No help found:"));
          Serial.println(args);

        }
        return;
      }


      if (strcmp(command,"get") == 0) {
        if (strstr(args," ")) {
          Serial.println(F("400:Fail:Should not have spaces in get command"));
          return;
        }
        if (exists(args)) {
          const char * value = get(args);
          Serial.print(F("200:Found:"));
          Serial.println(value);
        } 
        else {
          Serial.println(F("404:Attribute Not Found:-"));
        }
        return;
      }

      if (strcmp(command,"set") == 0) {
        char * attribute = args;
        char * value = consume_token(args);
        Serial.print("Attribute:");
        Serial.println(attribute);
        Serial.print("Value:");
        Serial.println(value);
        int result = set(attribute, value); // Intended to be overridden, must provide a way to describe failure...
        if (result == 200) {
          Serial.println(F("200:Success:-"));
          return;
        }
        if (result == 404) {
          Serial.println(F("404:Attribute Not Found:-"));
          return;
        }
        return;

      }

      if (strcmp(command,"do") == 0) {
        char * funcname= args;
        char * value = consume_token(args);
        Serial.print("Funcname:");
        Serial.println(funcname);
        Serial.print("Value:");
        Serial.println(value);
        int result = callfunc(funcname, value); // Intended to be overridden, must provide a way to describe failure...
        if (result == 200) {
          Serial.println(F("200:Success:-"));
          return;
        }
        if (result == 404) {
          Serial.println(F("404:funcname Not Found:-"));
          return;
        }
        return;

      }
    }
  }

  void run_host() {
    buffer_serial(); // Would be nice to have this with a timeout!
    // Would enable the thing to run more or less independently of the command host...
    // Mind you, max data rate is about a character per millisecond, so maybe just "nice"
    interpret_line();
  }

  virtual void setup() {
      Serial.begin(9600);
      while (!Serial) {
        ; // wait for serial port to connect. Needed for Leonardo only
      }
      Serial.print("DEV ");
      Serial.print( hostid()); // Name of the device. May or may note be used on the network verbatim
      Serial.print(" "); 
      // Ideally also want a sufficiently unique id here.
      Serial.println("OK");
  }
};

const int LEFT_MOTOR_DIR_PIN = 7;
const int LEFT_MOTOR_PWM_PIN = 9;
const int RIGHT_MOTOR_DIR_PIN = 8;
const int RIGHT_MOTOR_PWM_PIN = 10;

const int LED_PIN = 13;

const int DRIVE_FORWARD_TIME_MS = 1500;
const int TURN_TIME_MS = 2000;


class BotHost : public CommandHost {
private:
  int drive_forward_time_ms; // Forward distance
  int turn_time_ms; // 
  char temp_str[128];
public:
  BotHost() : drive_forward_time_ms(DRIVE_FORWARD_TIME_MS), turn_time_ms(TURN_TIME_MS) { }
  ~BotHost() { }


  const char *hostid() { 
    return "sumobot";
  }
  const char * attrs() {
    return "drive_forward_time_ms:int,turn_time_ms:int";
  }
  const char * funcs() { // need to implement on/off(!)
    return "forward,backward,left,right,on,off";
  }
  bool has_help(char * name) {
    if (strcmp(name,"drive_forward_time_ms")==0) return true;
    if (strcmp(name,"turn_time_ms")==0) return true;
    if (strcmp(name,"on")==0) return true;
    if (strcmp(name,"off")==0) return true;
    return false;
  }
  const char *help(char * name) {
    if (strcmp(name,"drive_forward_time_ms")==0) return "How long to move forward";
    if (strcmp(name,"turn_time_ms")==0) return "How long to turn";
    return "-";
  }
  bool exists(char * attribute) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) return true;
    if (strcmp(attribute,"turn_time_ms")==0) return true;
    return false;
  }
  const char *get(char * attribute) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) { 
      itoa (drive_forward_time_ms, temp_str, 10); 
      return temp_str; 
    }
    if (strcmp(attribute,"turn_time_ms")==0) { 
      itoa (turn_time_ms, temp_str, 10); 
      return temp_str; 
    }
    return "-";
  }
  int set(char* attribute, char* raw_value) {
    if (strcmp(attribute,"drive_forward_time_ms")==0) {
      int value = atoi(raw_value);
      drive_forward_time_ms = value;
      return 200;
    }
    if (strcmp(attribute,"turn_time_ms")==0) {
      int value = atoi(raw_value);
      turn_time_ms = value;
      return 200;
    }
    return 404;
  }
  int callfunc(char* funcname, char* raw_args) { 
    if (strcmp(funcname,"forward")==0) {
      forward();
      return 200;
    }
    if (strcmp(funcname,"backward")==0) {
      backward();
      return 200;
    }
    if (strcmp(funcname,"left")==0) {
      left();
      return 200;
    }
    if (strcmp(funcname,"right")==0) {
      right();
      return 200;
    }
    return 404; 
  }
  void stop(void) {
    analogWrite( LEFT_MOTOR_PWM_PIN, 0 );
    analogWrite( RIGHT_MOTOR_PWM_PIN, 0 );
  }
  void forward(void) {
    digitalWrite(LED_PIN, HIGH);   // Turn LED on while going forward
    digitalWrite( LEFT_MOTOR_DIR_PIN, HIGH );
    digitalWrite( RIGHT_MOTOR_DIR_PIN, HIGH );
    analogWrite( LEFT_MOTOR_PWM_PIN, 255 );
    analogWrite( RIGHT_MOTOR_PWM_PIN, 255 );
    delay( drive_forward_time_ms );
    stop();
  }
  void backward(void) {
    digitalWrite(LED_PIN, HIGH);   // Turn LED on while going forward
    digitalWrite( LEFT_MOTOR_DIR_PIN, LOW );
    digitalWrite( RIGHT_MOTOR_DIR_PIN, LOW );
    analogWrite( LEFT_MOTOR_PWM_PIN, 255 );
    analogWrite( RIGHT_MOTOR_PWM_PIN, 255 );
    delay( drive_forward_time_ms );
    stop();
  }
  void right(void) {
    digitalWrite(LED_PIN, LOW);   // Turn LED off while turning
    digitalWrite( LEFT_MOTOR_DIR_PIN, HIGH );
    digitalWrite( RIGHT_MOTOR_DIR_PIN, LOW );
    analogWrite( LEFT_MOTOR_PWM_PIN, 255 );
    analogWrite( RIGHT_MOTOR_PWM_PIN, 255 );
    delay( turn_time_ms );
    stop();
  }
  void left(void) {
    digitalWrite(LED_PIN, LOW);   // Turn LED off while turning
    digitalWrite( LEFT_MOTOR_DIR_PIN, LOW );
    digitalWrite( RIGHT_MOTOR_DIR_PIN, HIGH );
    analogWrite( LEFT_MOTOR_PWM_PIN, 255 );
    analogWrite( RIGHT_MOTOR_PWM_PIN, 255 );
    delay( turn_time_ms );
    stop();
  }

  void setup(void) {
      // Setup the pins
      CommandHost::setup();

      pinMode( LEFT_MOTOR_DIR_PIN, OUTPUT );
      pinMode( LEFT_MOTOR_PWM_PIN, OUTPUT );
      pinMode( RIGHT_MOTOR_DIR_PIN, OUTPUT );
      pinMode( RIGHT_MOTOR_PWM_PIN, OUTPUT );

      pinMode(LED_PIN, OUTPUT);
  }
};

BotHost MyCommandHost;

//----------------------------------------------------------
void setup()
{
  MyCommandHost.setup();
}

//----------------------------------------------------------
void loop()
{
  MyCommandHost.run_host();
}


