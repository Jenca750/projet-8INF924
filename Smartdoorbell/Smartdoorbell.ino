#include "config.h"
#include "wifi_api.h"
#include "button.h"
#include "sensor_ir.h"
#include "sensor_sound.h"

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("=== Smart Doorbell ESP32 ===");

  setupButton();
  setupIR();
  setupSound();

  //connectWiFi();
}

void loop() {
  handleButton();
  handleIR();
  handleSound();
}