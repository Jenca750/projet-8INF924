#ifndef CONFIG_H
#define CONFIG_H

// WiFi
#define WIFI_SSID "OPAL-2.4G"
#define WIFI_PASSWORD "ZAmRr9jBjRFYC273C5wT"

// API backend
#define API_URL "http://192.168.8.156:8000/api/events"
#define AUDIO_URL "http://192.168.8.156:8000/api/sound"
#define API_TOKEN "3f6a92c6f75b9b7343ac8c72e6215e07"

// Pins FireBeetle ESP32-E
#define BUTTON_PIN D6
#define TOUCH_PIN D7
#define IR_PIN D10
#define SPEAKER_PIN D2
#define US_PIN A3
#define SOUND_PIN A2

#define SOUND_THRESHOLD 500
#define SONIC_THRESHOLD 500

#endif  