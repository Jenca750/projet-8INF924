#ifndef CONFIG_H
#define CONFIG_H

// WiFi
#define WIFI_SSID ""
#define WIFI_PASSWORD ""

// API backend
#define API_URL "http://172.16.11.15:8000/api/events"
#define API_TOKEN "710829b8eb7e2e3991822d3711e9b6c3"

// Pins FireBeetle ESP32-E
#define BUTTON_PIN D6
#define IR_PIN D10
#define SPEAKER_PIN D5
#define US_PIN A3
#define SOUND_PIN A2

#define SOUND_THRESHOLD 500
#define SONIC_THRESHOLD 500

#endif  