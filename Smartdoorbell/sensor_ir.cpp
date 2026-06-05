#include <Arduino.h>
#include "config.h"
#include "wifi_api.h"

void setupIR() {
  pinMode(IR_PIN, INPUT);
  Serial.println("Capteur IR initialisé.");
}

void handleIR() {
  int detection = digitalRead(IR_PIN);

  if (detection == HIGH) {
    Serial.println("!!! MOUVEMENT DÉTECTÉ !!!");
    //sendEvent("motion");
    delay(500); // Évite de flooder le moniteur
  }
}