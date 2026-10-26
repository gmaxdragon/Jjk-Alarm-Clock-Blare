#pragma once
#include "Arduino.h"
constexpr uint16_t ST77XX_WHITE=0xFFFF,ST77XX_BLACK=0;
class Adafruit_GFX {
 public:
 void fillScreen(uint16_t);void drawFastHLine(int,int,int,uint16_t);
 void setTextWrap(bool);void setTextSize(int);void setTextColor(uint16_t);
 void setCursor(int,int);void print(const char*);void print(const String&);
 void fillRect(int,int,int,int,uint16_t);
};
