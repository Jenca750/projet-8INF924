#include <LittleFS.h>

#include <Arduino.h>
#include "speaker.h"
#include "config.h"

void setupSpeaker() {
  pinMode(SPEAKER_PIN, OUTPUT);
  noTone(SPEAKER_PIN);
  Serial.println("Speaker initialisé.");
}

void playDoorbellSound() {
  tone(SPEAKER_PIN, 784);
  delay(180);
  noTone(SPEAKER_PIN);
  delay(80);

  tone(SPEAKER_PIN, 988);
  delay(180);
  noTone(SPEAKER_PIN);
  delay(80);

  tone(SPEAKER_PIN, 1175);
  delay(300);
  noTone(SPEAKER_PIN);
}