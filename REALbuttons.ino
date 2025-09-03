#include "Adafruit_seesaw.h"

#define DEFAULT_I2C_ADDR 0x3A

uint8_t switches[4] = {18, 19, 20, 2};   // Seesaw button inputs
uint8_t pwms[4]    = {12, 13, 0, 1};     // Seesaw LED outputs

Adafruit_seesaw ss;

// Track button states
bool lastState[4] = {HIGH, HIGH, HIGH, HIGH}; // HIGH = not pressed (due to INPUT_PULLUP)
unsigned long pressStart[4] = {0, 0, 0, 0};

// Track LED states
bool ledActive[4] = {false, false, false, false};

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  if (!ss.begin(DEFAULT_I2C_ADDR)) {
    Serial.println(F("seesaw not found!"));
    while (1) delay(10);
  }

  for (uint8_t i = 0; i < 4; i++) {
    ss.pinMode(switches[i], INPUT_PULLUP);
    ss.analogWrite(pwms[i], 0);  // all LEDs off
    ledActive[i] = false;
  }

  Serial.println("Ready!");
}

void loop() {
  // --- 1. Check for serial commands from Python ---
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("LED_")) {
      int index = command.charAt(4) - '1';  // "LED_1" → index 0
      if (index >= 0 && index < 4) {
        if (command.endsWith("_ON")) {
          ss.analogWrite(pwms[index], 255);
          ledActive[index] = true;
          Serial.print("LED ");
          Serial.print(index + 1);
          Serial.println(" ON");
        } else if (command.endsWith("_OFF")) {
          ss.analogWrite(pwms[index], 0);
          ledActive[index] = false;
          Serial.print("LED ");
          Serial.print(index + 1);
          Serial.println(" OFF");
        }
      }
    }
  }

  // --- 2. Check button states ---
  for (uint8_t i = 0; i < 4; i++) {
    bool current = ss.digitalRead(switches[i]); // LOW = pressed

    // Button pressed
    if (current == LOW && lastState[i] == HIGH) {
      pressStart[i] = millis();
      Serial.print("button_");
      Serial.print(i + 1);
      Serial.print("_pressed ");
      Serial.println(pressStart[i]);
      lastState[i] = LOW;

      // Turn off LED if it was lit
      if (ledActive[i]) {
        ss.analogWrite(pwms[i], 0);
        ledActive[i] = false;
      }
    }

    // Button released
    else if (current == HIGH && lastState[i] == LOW) {
      unsigned long pressEnd = millis();
      Serial.print("button_");
      Serial.print(i + 1);
      Serial.print("_released ");
      Serial.println(pressEnd);
      lastState[i] = HIGH;
    }
  }

  delay(5); // debounce
}
