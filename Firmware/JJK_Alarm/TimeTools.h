#pragma once
#include <stdint.h>

namespace jjk {
// Uses unsigned millis() deltas, so counter wrap is well-defined for spans
// shorter than 2^31 ms. Does not require Wi-Fi, RTC or another component.
struct Countdown {
  uint8_t minutes=5;
  uint32_t remainingMs=300000UL;
  uint32_t startedMs=0;
  bool running=false;
  bool finished=false;
  void chooseMinutes(int v) {
    if(running)return;
    if(v<1)v=90;
    if(v>90)v=1;
    minutes=static_cast<uint8_t>(v);
    remainingMs=uint32_t(minutes)*60000UL;
    finished=false;
  }
  uint32_t left(uint32_t now) const {
    if(!running)return remainingMs;
    uint32_t passed=now-startedMs;
    return passed>=remainingMs?0:remainingMs-passed;
  }
  void pauseOrResume(uint32_t now) {
    if(running){remainingMs=left(now);running=false;return;}
    if(finished||remainingMs==0){
      remainingMs=uint32_t(minutes)*60000UL;
      finished=false;
    }
    startedMs=now;running=true;
  }
  void reset(){running=false;finished=false;remainingMs=uint32_t(minutes)*60000UL;}
  bool tick(uint32_t now){
    if(running&&left(now)==0){
      running=false;remainingMs=0;finished=true;return true;
    }
    return false;
  }
};
struct Stopwatch {
  uint32_t heldMs=0,startedMs=0;
  bool running=false;
  void pauseOrResume(uint32_t now){
    if(running){heldMs+=now-startedMs;running=false;}
    else{startedMs=now;running=true;}
  }
  uint32_t elapsed(uint32_t now) const {
    return heldMs+(running?now-startedMs:0);
  }
  void reset(){heldMs=0;running=false;}
};
} // namespace jjk
