// Robot Spoke for a constrained device

#include <CommandHostTiny.h>

const int LEFT_MOTOR_DIR_PIN = 7;
const int LEFT_MOTOR_PWM_PIN = 9;
const int RIGHT_MOTOR_DIR_PIN = 8;
const int RIGHT_MOTOR_PWM_PIN = 10;

const int LED_PIN = 13;

const int DRIVE_FORWARD_TIME_MS = 1500;
const int TURN_TIME_MS = 2000;


class BotHost : public CommandHostTiny {
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
    if (strcmp(funcname,"forward")==0) { forward(); return 200; }
    if (strcmp(funcname,"backward")==0) { backward(); return 200; }
    if (strcmp(funcname,"left")==0) { left(); return 200; }
    if (strcmp(funcname,"right")==0) { right(); return 200; }
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
      CommandHostTiny::setup();

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

