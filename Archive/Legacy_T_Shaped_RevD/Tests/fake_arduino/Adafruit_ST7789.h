#pragma once
#include "Adafruit_GFX.h"
class Adafruit_ST7789: public Adafruit_GFX {
 protected:
  int _colstart=0,_colstart2=0,_rowstart=0,_rowstart2=0;
 public:
  Adafruit_ST7789(int,int,int,int,int);
  void init(int,int);void invertDisplay(bool);void setRotation(int);
};
