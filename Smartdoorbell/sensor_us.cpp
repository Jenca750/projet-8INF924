#include <Arduino.h>
#include "sensor_us.h"
#include "config.h"
#include "wifi_api.h"

void setupUS() {
  pinMode(US_PIN, INPUT);
  Serial.println("Capteur ultrasonic initialisé.");
}

void handleUS() {
  int value = analogRead(US_PIN);
  float distance = value*(520/4095.0);

  if(distance < 20.0){
    Serial.println("!!! MOUVEMENT DÉTECTÉ !!!");
    Serial.println(distance);
    sendEvent("motion");
    delay(500);
  }
  

  

  delay(100);
}