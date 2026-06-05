#include "config.h"
#include "wifi_api.h"
#include "button.h"
#include "sensor_ir.h"
#include "sensor_us.h"
#include "sensor_sound.h"
#include "speaker.h"

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("=== Smart Doorbell ESP32 ===");

  setupButton();
  setupIR();
  setupSound();
  setupUS();
  setupSpeaker();

  //connectWiFi();  
}

void loop() {
  handleButton();
  handleUS();
  handleSound();
}