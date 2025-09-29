#include <Servo.h>

Servo tipper;
const int servoPin = 9;
const int stepSize = 2;    // degrees per step (smaller = smoother, but slower)
const int stepDelay = 10;  // ms delay between steps

void setup() {
  Serial.begin(115200);
  tipper.attach(servoPin);
  tipper.write(0);
}

void smoothMove(int fromAngle, int toAngle) {
  int dir = (toAngle > fromAngle) ? 1 : -1;
  for (int pos = fromAngle; pos != toAngle; pos += dir * stepSize) {
    tipper.write(pos);
    delay(stepDelay);
  }
  tipper.write(toAngle);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'T') {
      smoothMove(0, 180);
      delay(3000);
      smoothMove(180, 0);
    }
  }
}
