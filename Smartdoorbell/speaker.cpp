#include <Arduino.h>
#include "speaker.h"
#include "config.h"
#include "wifi_api.h"

void setupSpeaker() {
  pinMode(SPEAKER_PIN, OUTPUT);
  noTone(SPEAKER_PIN);
  Serial.println("Speaker initialisé.");
}

void playDoorbellSound() {
  tone(SPEAKER_PIN, 1000);
  delay(100);
  noTone(SPEAKER_PIN);
  streamAudio(AUDIO_URL);
}