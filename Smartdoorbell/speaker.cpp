#include <Arduino.h>
#include "speaker.h"
#include "config.h"
#include "wifi_api.h"

void setupSpeaker() {
  pinMode(SPEAKER_PIN, OUTPUT);
  noTone(SPEAKER_PIN);
  Serial.println("Speaker initialisé.");
}

void playFallbackRing() {
  Serial.println("Sonnerie de secours...");
  
  tone(SPEAKER_PIN, 1047); delay(200); // Do5
  noTone(SPEAKER_PIN);     delay(50);
  tone(SPEAKER_PIN, 880);  delay(200); // La4
  noTone(SPEAKER_PIN);     delay(50);
  tone(SPEAKER_PIN, 784);  delay(400); // Sol4
  noTone(SPEAKER_PIN);     delay(150);
  
  tone(SPEAKER_PIN, 784);  delay(200); // Sol4
  noTone(SPEAKER_PIN);     delay(50);
  tone(SPEAKER_PIN, 880);  delay(200); // La4
  noTone(SPEAKER_PIN);     delay(50);
  tone(SPEAKER_PIN, 1047); delay(400); // Do5
  noTone(SPEAKER_PIN);
}

void playDoorbellSound() {
  tone(SPEAKER_PIN, 1000);
  delay(100);
  noTone(SPEAKER_PIN);
  streamAudio(AUDIO_URL);
}