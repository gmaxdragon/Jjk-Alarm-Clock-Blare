#pragma once
#include "Arduino.h"
#include <functional>
constexpr int HTTP_GET=1,HTTP_POST=2;
class WebServer {
 public:
 explicit WebServer(int){}
 void on(const char*,int,std::function<void()>);
 void onNotFound(std::function<void()>);
 void send(int,const char*,const String&);
 void sendHeader(const char*,const char*,bool);
 String arg(const char*);
 bool hasArg(const char*);
 void begin();void handleClient();
};
