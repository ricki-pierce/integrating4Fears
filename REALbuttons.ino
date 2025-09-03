// Include the Adafruit Seesaw library, which lets the Arduino talk to the Seesaw chip
#include "Adafruit_seesaw.h"

// Define the default I2C address for the Seesaw device (needed for communication)
#define DEFAULT_I2C_ADDR 0x3A

// Define which Seesaw pins are connected to the 4 push buttons
uint8_t switches[4] = {18, 19, 20, 2};   // Seesaw button inputs

// Define which Seesaw pins are connected to the 4 LEDs
uint8_t pwms[4]    = {12, 13, 0, 1};     // Seesaw LED outputs

// Create an object to talk to the Seesaw chip
Adafruit_seesaw ss;

// Track the last known state of each button
// HIGH means "not pressed" because the pins use INPUT_PULLUP
bool lastState[4] = {HIGH, HIGH, HIGH, HIGH};

// Record the time when each button was pressed
unsigned long pressStart[4] = {0, 0, 0, 0};

// Track whether each LED is currently on or off
bool ledActive[4] = {false, false, false, false};

void setup() {
  // Start communication with the computer at 115200 baud
  Serial.begin(115200);
  
  // Wait until the serial monitor is ready (useful for some boards)
  while (!Serial) delay(10);

  // Try to start communication with the Seesaw chip
  if (!ss.begin(DEFAULT_I2C_ADDR)) {
    // If it can’t be found, print an error message and stop the program
    Serial.println(F("seesaw not found!"));
    while (1) delay(10);
  }

  // Set up each button and LED
  for (uint8_t i = 0; i < 4; i++) {
    // Configure each button pin as an input with pull-up enabled
    ss.pinMode(switches[i], INPUT_PULLUP);

    // Make sure each LED starts turned off
    ss.analogWrite(pwms[i], 0);
    ledActive[i] = false;
  }

  // Tell the computer everything is ready
  Serial.println("Ready!");
}

void loop() {
  // --- 1. Check if any commands were sent from the computer (like from Python) ---
  if (Serial.available() > 0) {
    // Read the text sent from the computer until a newline character
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any extra spaces or newlines

    // If the command starts with "LED_", then it’s meant to control an LED
    if (command.startsWith("LED_")) {
      // Figure out which LED number was mentioned ("LED_1" → index 0, etc.)
      int index = command.charAt(4) - '1';

      // Make sure the number is valid (between 0 and 3)
      if (index >= 0 && index < 4) {
        // If the command ends with "_ON", turn the LED on
        if (command.endsWith("_ON")) {
          ss.analogWrite(pwms[index], 255);  // Full brightness
          ledActive[index] = true;           // Remember it’s on
          Serial.print("LED ");
          Serial.print(index + 1);
          Serial.println(" ON");
        } 
        // If the command ends with "_OFF", turn the LED off
        else if (command.endsWith("_OFF")) {
          ss.analogWrite(pwms[index], 0);    // Off
          ledActive[index] = false;          // Remember it’s off
          Serial.print("LED ");
          Serial.print(index + 1);
          Serial.println(" OFF");
        }
      }
    }
  }

  // --- 2. Check the state of each button ---
  for (uint8_t i = 0; i < 4; i++) {
    // Read the current state of the button (LOW = pressed, HIGH = not pressed)
    bool current = ss.digitalRead(switches[i]);

    // --- Case A: Button was just pressed ---
    if (current == LOW && lastState[i] == HIGH) {
      // Record the exact time the button was pressed
      pressStart[i] = millis();
      
      // Send a message to the computer that the button was pressed
      Serial.print("button_");
      Serial.print(i + 1);
      Serial.print("_pressed ");
      Serial.println(pressStart[i]);
      
      // Update the stored state to "pressed"
      lastState[i] = LOW;

      // If the LED was on when pressed, turn it off
      if (ledActive[i]) {
        ss.analogWrite(pwms[i], 0);
        ledActive[i] = false;
      }
    }

    // --- Case B: Button was just released ---
    else if (current == HIGH && lastState[i] == LOW) {
      // Record the time the button was released
      unsigned long pressEnd = millis();
      
      // Send a message to the computer that the button was released
      Serial.print("button_");
      Serial.print(i + 1);
      Serial.print("_released ");
      Serial.println(pressEnd);
      
      // Update the stored state to "not pressed"
      lastState[i] = HIGH;
    }
  }

  // Small delay to prevent detecting noise from button presses (debouncing)
  delay(5);
}
