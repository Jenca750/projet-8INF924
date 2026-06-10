#ifndef WIFI_API_H
#define WIFI_API_H

void connectWiFi();
void sendEvent(const char* eventType);
void streamAudio(const char* url);

#endif