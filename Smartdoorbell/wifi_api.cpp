#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "wifi_api.h"
#include "speaker.h"

void connectWiFi() {
  Serial.print("Connexion WiFi à ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi connecté !");
    Serial.print("IP ESP32 : ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("Échec connexion WiFi.");
  }
}

void sendEvent(const char* eventType) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi non connecté, tentative de reconnexion...");
    connectWiFi();

    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Impossible d'envoyer l'événement.");
      return;
    }
  }

  HTTPClient http;
  http.begin(API_URL);

  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Bearer ") + API_TOKEN);

  StaticJsonDocument<256> doc;
  doc["event_type"] = eventType;

  String payload;
  serializeJson(doc, payload);

  Serial.print("Envoi JSON : ");
  Serial.println(payload);

  int httpCode = http.POST(payload);

  Serial.print("Réponse HTTP : ");
  Serial.println(httpCode);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.println("Réponse serveur :");
    Serial.println(response);
  } else {
    Serial.print("Erreur HTTPClient : ");
    Serial.println(http.errorToString(httpCode));
  }

  http.end();
}

void streamAudio(const char* url) {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) {
      playFallbackRing();
      return;
    }
  }

  HTTPClient http;
  http.begin(url);
  http.addHeader("Authorization", String("Bearer ") + API_TOKEN);

  int httpCode = http.GET();

  if (httpCode != 200) {
    http.end();
    playFallbackRing();
    return;
  }
  int totalLen = http.getSize();

  WiFiClient* stream = http.getStreamPtr();

  // Skip WAV header (44 bytes)
  uint8_t header[44];
  stream->readBytes(header, 44);
  int remaining = totalLen - 44;

  uint8_t buf[1024];

  while (remaining > 0) {
    int toRead = min((int)sizeof(buf), remaining);
    int bytesRead = stream->readBytes(buf, toRead);

    if (bytesRead <= 0) {
      playFallbackRing();
      break;
    }

    float gain = 4.0;

    for (int i = 44; i + 1 < bytesRead; i += 2) {
        int16_t sample = (int16_t)(buf[i] | (buf[i + 1] << 8));
        
        // Gain numérique
        int32_t amplified = (int32_t)(sample * gain);
        
        // Clipping
        if (amplified > 32767) amplified = 32767;
        if (amplified < -32768) amplified = -32768;

        uint8_t dacVal = (uint8_t)((amplified + 32768) >> 8);
        dacWrite(SPEAKER_PIN, dacVal);
        delayMicroseconds(125);
    }

    remaining -= bytesRead;
  }

  dacWrite(SPEAKER_PIN, 128); // silence
  http.end();
}