#pragma once
#include "Arduino.h"
constexpr int WL_CONNECTED=3,WIFI_STA=1,WIFI_OFF=0;
struct WiFiIP {String toString() const;};
struct FakeWiFi {int status();void begin(const char*,const char*);void setAutoReconnect(bool);void disconnect();void mode(int);WiFiIP localIP();};
extern FakeWiFi WiFi;
