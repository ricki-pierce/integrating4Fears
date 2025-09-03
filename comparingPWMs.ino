/*
 * This is a stand alone sketch. It does not require Python companion. 
 * This sketch is designed to demonstrate how different LED brightness levels look 
 * when controlled using PWM (Pulse Width Modulation). 
 * Each of the four arcade-style buttons has an LED that starts off at 0 PWM, and every time you press a button, 
 * its LED gets brighter in steps. The first press increases brightness by a larger amount, 
 * and subsequent presses increase it more slowly. When the LED reaches full brightness, it resets to off. 
 * All brightness levels are printed to the Serial Monitor so you can see the numeric PWM values as well.

 */

// Include the main library for Adafruit seesaw (handles I2C communication and button/LED control)
#include "Adafruit_seesaw.h"

// Include additional helper library for NeoPixel (LED) functionality (not strictly used here but required for some features)
#include <seesaw_neopixel.h>

// Define the default I2C address for the seesaw device (used to communicate with it)
#define  DEFAULT_I2C_ADDR 0x3A

// Define which pins are connected to each of the 4 arcade buttons
#define  SWITCH1  18
#define  SWITCH2  19
#define  SWITCH3  20
#define  SWITCH4  2

// Define which pins control the PWM (LED brightness) for each button
#define  PWM1  12
#define  PWM2  13
#define  PWM3  0
#define  PWM4  1

// Create an object "ss" to interact with the seesaw board
Adafruit_seesaw ss;

// Array to store the current PWM (brightness) value of each LED/button
uint16_t pwmValues[4] = {0, 0, 0, 0};

// Array to track if this is the first press of each button (used for larger first increment)
bool firstIncrement[4] = {true, true, true, true};

// The setup function runs once when the Arduino starts
void setup() {
  Serial.begin(115200);           // Start the serial monitor at 115200 baud
  while (!Serial) delay(10);      // Wait for serial connection (useful for some boards)

  Serial.println(F("Adafruit PID 5296 I2C QT 4x LED Arcade Buttons test!")); // Print intro message

  // Initialize seesaw board, check if it is connected
  if (!ss.begin(DEFAULT_I2C_ADDR)) {
    Serial.println(F("seesaw not found!")); // Print error if board not found
    while(1) delay(10);                      // Stop program if seesaw is missing
  }

  // Setup each button pin as an input with internal pull-up resistor
  // This means the pin reads HIGH when not pressed and LOW when pressed
  ss.pinMode(SWITCH1, INPUT_PULLUP);
  ss.pinMode(SWITCH2, INPUT_PULLUP);
  ss.pinMode(SWITCH3, INPUT_PULLUP);
  ss.pinMode(SWITCH4, INPUT_PULLUP);

  // Set all LEDs to initial PWM (brightness) of 0 (off)
  ss.analogWrite(PWM1, pwmValues[0]);
  ss.analogWrite(PWM2, pwmValues[1]);
  ss.analogWrite(PWM3, pwmValues[2]);
  ss.analogWrite(PWM4, pwmValues[3]);

  // Print initial brightness of all buttons to serial monitor
  Serial.print("Initial brightness: ");
  printPWMValues();
}

// Function to print current PWM (brightness) values of all buttons
void printPWMValues() {
  Serial.print(pwmValues[0]); Serial.print("\t"); // Print first button value, followed by a tab
  Serial.print(pwmValues[1]); Serial.print("\t"); // Print second button value, followed by a tab
  Serial.print(pwmValues[2]); Serial.print("\t"); // Print third button value, followed by a tab
  Serial.println(pwmValues[3]);                   // Print fourth button value, then move to next line
}

// Function to check if a button is pressed and update LED brightness
void handleButton(uint8_t buttonIndex, uint8_t switchPin, uint8_t pwmPin) {
  if (!ss.digitalRead(switchPin)) { // Check if button is pressed (LOW because of pull-up)
    ss.analogWrite(pwmPin, pwmValues[buttonIndex]); // Update LED to current brightness

    // Increase PWM value
    if (firstIncrement[buttonIndex]) {  
      pwmValues[buttonIndex] += 25;       // First press increases brightness by 55
      firstIncrement[buttonIndex] = false; // Mark first press as done
    } else {
      pwmValues[buttonIndex] += 15;       // Subsequent presses increase by 15
    }

    // Reset PWM if it goes above 255 (max value for LED brightness)
    if (pwmValues[buttonIndex] > 255) {
      pwmValues[buttonIndex] = 0;         // Reset brightness back to 0
      firstIncrement[buttonIndex] = true; // Reset first press flag
    }

    printPWMValues(); // Show updated brightness in serial monitor

    delay(250); // Small delay to avoid reading button multiple times too quickly (debounce)
  }
}

// Main loop runs repeatedly after setup
void loop() {
  // Check each button and update its LED
  handleButton(0, SWITCH1, PWM1);
  handleButton(1, SWITCH2, PWM2);
  handleButton(2, SWITCH3, PWM3);
  handleButton(3, SWITCH4, PWM4);

  delay(10); // Tiny delay to make loop stable
}
