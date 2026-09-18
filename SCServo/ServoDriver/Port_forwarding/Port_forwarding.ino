#include <HardwareSerial.h>

// Define the pins used internally by the Waveshare board for the servos
#define RX_PIN 18
#define TX_PIN 19

void setup() {
  // 1. Start USB Serial (Connected to your PC/Python)
  // Must match the baudrate in your Python script
  Serial.begin(1000000); 

  // 2. Start Servo Serial (Connected to the STS3215 motors)
  // Must match the baudrate of the motors (Default is 1000000)
  Serial1.begin(1000000, SERIAL_8N1, RX_PIN, TX_PIN);
}

void loop() {
  // Forward data: PC -> ESP32 -> Servo
  if (Serial.available()) {
    Serial1.write(Serial.read());
  }

  // Forward data: Servo -> ESP32 -> PC
  if (Serial1.available()) {
    Serial.write(Serial1.read());
  }
}