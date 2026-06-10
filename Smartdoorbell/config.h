#ifndef CONFIG_H
#define CONFIG_H

// WiFi
#define WIFI_SSID "BELL415"
#define WIFI_PASSWORD "6695A47EA425"

// API backend
#define API_URL "http://192.168.2.107:8000/api/events"
#define AUDIO_URL "http://192.168.2.107:8000/api/sound"
#define API_TOKEN "212f00c915ed8c3806ca8b796832ac76"

// Pins FireBeetle ESP32-E
#define BUTTON_PIN D6
#define IR_PIN D10
#define SPEAKER_PIN D2
#define US_PIN A3
#define SOUND_PIN A2

#define SOUND_THRESHOLD 500
#define SONIC_THRESHOLD 500

#endif  