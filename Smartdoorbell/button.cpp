#include <Arduino.h>

#include "config.h"
#include "button.h"
#include "wifi_api.h"
#include "speaker.h"

bool lastButtonState = LOW;
unsigned long lastButtonTime = 0;

const unsigned long debounceDelay = 300;

void setupButton() {
  pinMode(BUTTON_PIN, INPUT);

  lastButtonState = digitalRead(BUTTON_PIN);

  Serial.println("Bouton initialisé.");
}

void handleButton() {
  bool currentState = digitalRead(BUTTON_PIN);

  if (currentState == LOW && lastButtonState == HIGH) {
    unsigned long now = millis();

    if (now - lastButtonTime > debounceDelay) {
      Serial.println("Bouton appuyé -> envoi événement button");
      sendEvent("button");
      playDoorbellSound();
      lastButtonTime = now;
    }
  }

  lastButtonState = currentState;
}