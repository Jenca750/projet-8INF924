#include "config.h"
#include "wifi_api.h"

#include "button.h"
#include "sensor_us.h"
#include "sensor_ir.h"
#include "speaker.h"
#include "touch_button.h"

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("=== Smart Doorbell ESP32 ===");

  setupButton();
  setupTouchButton();
  setupUS();
  setupSpeaker();

  connectWiFi();  
}

void loop() {
  handleButton();
  handleUS();
  handleTouchButton();
}