#include <Arduino.h>
#include "sensor_us.h"
#include "config.h"
#include "wifi_api.h"

void setupUS() {
  pinMode(US_PIN, INPUT);
  Serial.println("Capteur ultrasonic initialisé.");
}

bool validateUS() {
  int validCount = 0;

  for (int i = 0; i < 3; i++) {
    int value = analogRead(US_PIN);

    Serial.print("Ultrasonic : ");
    Serial.println(value);

    if (value > SONIC_THRESHOLD) {
      validCount++;
    }

    delay(20);
  }

  return validCount >= 3;
}

void handleUS() {
  int value = analogRead(US_PIN);

  if (value > SONIC_THRESHOLD) {
    Serial.println("!!! MOUVEMENT DÉTECTÉ !!!");
    //sendEvent("mouvement");
    delay(500);
  }

  delay(100);
}