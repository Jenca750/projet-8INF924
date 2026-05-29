#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "wifi_api.h"

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