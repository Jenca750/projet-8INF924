#include <Arduino.h>
#include "config.h"
#include "wifi_api.h"
#include "sensor_us.h"

void setupIR() {
  pinMode(IR_PIN, INPUT);
  Serial.println("Capteur IR initialisé.");
}

void handleIR() {
  int detection = digitalRead(IR_PIN);

  if (detection == HIGH) {
    Serial.println("!!! MOUVEMENT DÉTECTÉ !!!");
    //sendEvent("motion");  
    
    delay(500); 
  }
}