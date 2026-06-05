#include <Arduino.h>
#include "sensor_sound.h"
#include "config.h"
#include "wifi_api.h"

void setupSound() {
  pinMode(SOUND_PIN, INPUT);
  Serial.println("Capteur son initialisé.");
}

void handleSound() {
  int value = analogRead(SOUND_PIN);

  if (value > SOUND_THRESHOLD) {
    //Serial.println("!!! SON FORT DÉTECTÉ !!!");
    //sendEvent("sound");
    delay(500);
  }

  delay(100);
}