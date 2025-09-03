/*
  This Arduino code is standalone. It does not rely on any Python script.
  Upload it to your board to test the buttons. 

  How it works:
  - Only one LED lights up at a time.
  - When you press the corresponding button, the LED turns off.
  - Then a new random button (that hasn’t yet been pressed) lights up.
  - Repeat until all buttons have been pressed.
  - When all buttons are pressed, the game automatically resets and starts over.

  This Arduino code requires the Adafruit Seesaw and Adafruit BusIO libraries to be installed 
  in the Arduino IDE (can be installed via Library Manager). 

  The push buttons and LEDs should be assembled according to Adafruit’s guidelines. 
  The Seesaw pins corresponding to the buttons and LEDs are fixed and should not be changed 
  unless you intentionally want to deactivate them. 

  LEDs are set to full brightness by default (255). To make them dimmer, you can change the 
  255 values to any number between 0 (off) and 255 (full brightness).

  Hardware mapping (example, adjust to your wiring):
  
     Buttons             LEDs (PWM)
     ------              ----------
     Button/Switch 1 -> pin 18  LED 1 -> pin 12
     Button/Switch 2 -> pin 19  LED 2 -> pin 13
     Button/Switch 3 -> pin 20  LED 3 -> pin 0
     Button/Switch 4 -> pin 2   LED 4 -> pin 1
*/

#include "Adafruit_seesaw.h"  // Include the Adafruit seesaw library to control the seesaw board

#define DEFAULT_I2C_ADDR 0x3A  // Define the default I2C address of the seesaw board

uint8_t switches[4] = {18, 19, 20, 2}; // Array holding the pin numbers for 4 buttons
uint8_t pwms[4] = {12, 13, 0, 1};      // Array holding the pin numbers for 4 LEDs

Adafruit_seesaw ss; // Create an instance of the seesaw object to interact with the board

// Array to track which buttons have been pressed already (false = not pressed)
bool pressedFlags[4] = {false, false, false, false};

// Variable to track which button's LED is currently on (-1 = none)
int currentButton = -1;

void setup() {
  Serial.begin(115200);        // Start serial communication at 115200 baud
  while (!Serial) delay(10);   // Wait until serial is ready (for some boards)

  // Initialize the seesaw board
  if (!ss.begin(DEFAULT_I2C_ADDR)) {
    Serial.println(F("seesaw not found!")); // Print error if board is not detected
    while (1) delay(10);                     // Stop here forever if not found
  }

  // Loop through each button/LED pair
  for (uint8_t i = 0; i < 4; i++) {
    ss.pinMode(switches[i], INPUT_PULLUP); // Set button pins as input with pull-up resistor
    ss.analogWrite(pwms[i], 0);            // Turn off all LEDs initially
    pressedFlags[i] = false;               // Mark all buttons as not pressed
  }

  Serial.println("Ready! All buttons off."); // Let user know setup is complete
  randomSeed(analogRead(A0));                // Seed the random number generator using noise from analog pin A0
}

void loop() {
  // Check if all buttons have been pressed
  bool allPressed = true; // Assume all are pressed until we find one that isn't
  for (uint8_t i = 0; i < 4; i++) {
    if (!pressedFlags[i]) { // If any button hasn't been pressed
      allPressed = false;   // Not all pressed
      break;                // Stop checking further
    }
  }

  // If all buttons were pressed, reset the game
  if (allPressed) {
    Serial.println("All buttons pressed! Resetting...");
    for (uint8_t i = 0; i < 4; i++) {
      pressedFlags[i] = false;       // Reset pressed status
      ss.analogWrite(pwms[i], 0);    // Turn off all LEDs
    }
    currentButton = -1;               // No button currently lit
    delay(1000);                      // Wait 1 second before continuing
    return;                           // Skip rest of loop and start over
  }

  // If no button is currently lit, pick a random unpressed one
  if (currentButton == -1) {
    do {
      currentButton = random(0, 4);           // Pick a random number between 0 and 3
    } while (pressedFlags[currentButton]);    // Repeat if the chosen button was already pressed
    Serial.print("Lighting button ");
    Serial.println(currentButton + 1);       // Print which button is lit (1-based index)
    ss.analogWrite(pwms[currentButton], 255); // Turn on the LED for that button
  }

  // Check if the currently lit button has been pressed
  if (!ss.digitalRead(switches[currentButton])) { // LOW means the button is pressed
    Serial.print("Button ");
    Serial.print(currentButton + 1);
    Serial.println(" pressed!");              // Print which button was pressed
    ss.analogWrite(pwms[currentButton], 0);  // Turn off the LED
    pressedFlags[currentButton] = true;      // Mark this button as pressed
    currentButton = -1;                       // Reset currentButton for next round
    delay(2000);                              // Wait 2 seconds before lighting the next button
  }

  delay(10); // Small delay to debounce button press (prevent false readings)
}
