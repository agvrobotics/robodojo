#include <Servo.h>

Servo tipper;
const int servoPin = 9;
const int stepSize = 2;    // degrees per step (smaller = smoother, but slower)
const int stepDelay = 10;  // ms delay between steps

void setup() {
  Serial.begin(115200);
  tipper.attach(servoPin);
  tipper.write(0); // start down
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
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // Check for TIP command
    if (cmd.startsWith("TIP,")) {
      int commaIndex = cmd.indexOf(',');
      if (commaIndex > 0) {
        int action = cmd.substring(commaIndex + 1).toInt();
        int current = tipper.read(); // current position for smooth transition
        if (action == 1) {
          smoothMove(current, 180);
        } else if (action == 0) {
          smoothMove(current, 0);
        }
      }
    }
  }
}
