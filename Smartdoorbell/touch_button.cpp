#include <Arduino.h>

#include "config.h"
#include "touch_button.h"
#include "wifi_api.h"
#include "speaker.h"

bool lastTouchButtonState = LOW;
unsigned long lastTouchButtonTime = 0;

const unsigned long debounceDelay = 300;

void setupTouchButton() {
  pinMode(TOUCH_PIN, INPUT);

  lastTouchButtonState = digitalRead(TOUCH_PIN);

  Serial.println("Bouton touch initialisé.");
}

void handleTouchButton() {
  bool currentState = digitalRead(TOUCH_PIN);

  if (currentState == LOW && lastTouchButtonState == HIGH) {
    unsigned long now = millis();

    if (now - lastTouchButtonTime > debounceDelay) {
      Serial.println("Touch Bouton appuyé -> envoi événement button");
      sendEvent("button");
      playDoorbellSound();
      lastTouchButtonTime = now;
    }
  }

  lastTouchButtonState = currentState;
}