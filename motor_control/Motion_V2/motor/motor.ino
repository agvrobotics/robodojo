#include <Servo.h>

// ------------------- Encoder pins -------------------
// Left wheel encoder
#define ENCA_L 20
#define ENCB_L 21

// Right wheel encoder
#define ENCA_R 18
#define ENCB_R 19

// ------------------- Motor pins -------------------
#define ENA 5   // Left motor enable
#define ENB 6   // Right motor enable

#define IN1 30  // Left motor IN1
#define IN2 31  // Left motor IN2
#define IN3 32  // Right motor IN1
#define IN4 33  // Right motor IN2

//--------------------Tipper Setup--------------------
Servo tipper;
const int servoPin = 9;
const int stepSize = 2;
const int stepDelay = 10; 
int targetAngle = 0;
int currentAngle = 0;
unsigned long lastStepTime = 0;

// ------------------- Encoder counters -------------------
volatile long countL = 0;
volatile long countR = 0;

// ------------------- Timing -------------------
unsigned long lastReport = 0;
const unsigned long reportInterval = 50;

void setup() {
  // Motor pins
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Encoder interrupts
  attachInterrupt(digitalPinToInterrupt(ENCA_L), readEncoderL_A, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCB_L), readEncoderL_B, CHANGE);

  attachInterrupt(digitalPinToInterrupt(ENCA_R), readEncoderR_A, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCB_R), readEncoderR_B, CHANGE);

  // Servo
  tipper.attach(servoPin);
  tipper.write(0);

  Serial.begin(115200);
}

// ------------------- Main loop -------------------
void loop() {
  char buffer[32];
  if (Serial.available()) {
    int len = Serial.readBytesUntil('\n', buffer, sizeof(buffer) - 1);
    if (len > 0) {
      buffer[len] = '\0';

      if (strncmp(buffer, "VEL,", 4) == 0) {
        char *p = strtok(buffer + 4, ",");
        if (p) {
          float linear = atof(p);
          p = strtok(NULL, ",");
          if (p) {
            float angular = atof(p);
            setMotorPWM(linear, angular);
          }
        }
      }
      else if (strncmp(buffer, "TIP,", 4) == 0) {
        int action = atoi(buffer + 4);
        if (action == 1) targetAngle = 60;
        else if (action == 0) targetAngle = 0;
      }
    }
  }

  updateServo();

  if (millis() - lastReport >= reportInterval) {
    lastReport = millis();
    Serial.print(countL);
    Serial.print(",");
    Serial.println(countR);
  }
}

// ------------------- Convert cmd_vel to PWM -------------------
void setMotorPWM(float linear, float angular) {
  const float WHEEL_BASE = 0.2325;
  const int MAX_PWM = 255;

  const float MAX_LINEAR  = 0.425;
  const float MAX_ANGULAR = 2.99;

  // Clamp
  linear = constrain(linear, -MAX_LINEAR, MAX_LINEAR);
  angular = constrain(angular, -MAX_ANGULAR, MAX_ANGULAR);

  float v_left  = linear - (angular * WHEEL_BASE / 2.0);
  float v_right = linear + (angular * WHEEL_BASE / 2.0);

  int pwmL = constrain(int((v_left  / MAX_LINEAR) * MAX_PWM), -MAX_PWM, MAX_PWM);
  int pwmR = constrain(int((v_right / MAX_LINEAR) * MAX_PWM), -MAX_PWM, MAX_PWM);

  // Deadzone
  if (abs(pwmL) < 30) pwmL = 0;
  if (abs(pwmR) < 30) pwmR = 0;

  // Left motor
  if (pwmL >= 0) { digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); }
  else { digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); pwmL = -pwmL; }
  analogWrite(ENA, pwmL);

  // Right motor
  if (pwmR >= 0) { digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW); }
  else { digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); pwmR = -pwmR; }
  analogWrite(ENB, pwmR);
}

// ------------------- Servo update -------------------
void updateServo() {
  unsigned long now = millis();
  if (now - lastStepTime >= stepDelay) {
    lastStepTime = now;

    if (currentAngle < targetAngle) {
      currentAngle += stepSize;
      if (currentAngle > targetAngle) currentAngle = targetAngle;
      tipper.write(currentAngle);
    }
    else if (currentAngle > targetAngle) {
      currentAngle -= stepSize;
      if (currentAngle < targetAngle) currentAngle = targetAngle;
      tipper.write(currentAngle);
    }
  }
}

// ------------------- Encoder ISRs -------------------
void readEncoderL_A() { int a = digitalRead(ENCA_L), b = digitalRead(ENCB_L); if (a == b) countL++; else countL--; }
void readEncoderL_B() { int a = digitalRead(ENCA_L), b = digitalRead(ENCB_L); if (a != b) countL++; else countL--; }

void readEncoderR_A() { int a = digitalRead(ENCA_R), b = digitalRead(ENCB_R); if (a == b) countR++; else countR--; }
void readEncoderR_B() { int a = digitalRead(ENCA_R), b = digitalRead(ENCB_R); if (a != b) countR++; else countR--; }
