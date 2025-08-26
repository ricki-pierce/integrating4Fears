   // Button pins
const int buttonPins[4] = {5, 6, 7, 8};   // Up to 4 buttons on pins 5–8
// LED pins
const int ledPins[4] = {10, 11, 12, 13};  // Up to 4 LEDs on pins 10–13

// State tracking
bool lastState[4] = {LOW, LOW, LOW, LOW};       // Tracks whether each button was pressed or not
unsigned long pressStart[4] = {0, 0, 0, 0};     // Stores press times
bool ledActive[4] = {false, false, false, false}; // Track which LED is currently ON

void setup() {
  Serial.begin(9600);  

  for (int i = 0; i < 4; i++) {
    pinMode(buttonPins[i], INPUT);
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
}

void loop() {
  // --- 1. Check for serial commands from Python ---
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the command (e.g., "LED_2_ON")
    command.trim();

    if (command.startsWith("LED_")) {
      int ledIndex = command.charAt(4) - '1';  // Extract LED number (1-based → 0-based index)
      if (ledIndex >= 0 && ledIndex < 4) {
        // Turn that LED ON
        digitalWrite(ledPins[ledIndex], HIGH);
        ledActive[ledIndex] = true;
      }
    }
  }

  // --- 2. Check button states ---
  for (int i = 0; i < 4; i++) {
    bool current = digitalRead(buttonPins[i]);

    // Button pressed
    if (current == HIGH && lastState[i] == LOW) {
      pressStart[i] = millis();
      Serial.print("button_");
      Serial.print(i + 1);
      Serial.print("_pressed ");
      Serial.println(pressStart[i]);
      lastState[i] = HIGH;
    }

    // Button released
    else if (current == LOW && lastState[i] == HIGH) {
      unsigned long pressEnd = millis();
      Serial.print("button_");
      Serial.print(i + 1);
      Serial.print("_released ");
      Serial.println(pressEnd);
      lastState[i] = LOW;

      // If this button corresponds to the active LED, turn it OFF
      if (ledActive[i]) {
        digitalWrite(ledPins[i], LOW);
        ledActive[i] = false;
      }
    }
  }

  delay(5);  // Debounce
}
