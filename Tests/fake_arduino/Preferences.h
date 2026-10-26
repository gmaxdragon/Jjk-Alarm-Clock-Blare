#pragma once
#include "Arduino.h"
class Preferences {
 public:
 bool begin(const char*,bool);
 void putUChar(const char*,uint8_t);void putBool(const char*,bool);
 void putInt(const char*,int);void putString(const char*,const char*);
 uint8_t getUChar(const char*,uint8_t);bool getBool(const char*,bool);
 int getInt(const char*,int);String getString(const char*,const char*);
};
