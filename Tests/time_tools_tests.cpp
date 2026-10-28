#include "../Firmware/JJK_Alarm/TimeTools.h"
#include <cassert>
#include <iostream>
int main(){
  jjk::Countdown c;
  assert(c.minutes==5 && c.remainingMs==300000 && !c.running);
  c.chooseMinutes(1);assert(c.minutes==1 && c.left(111)==60000);
  c.pauseOrResume(0xfffff000UL);assert(c.running);
  assert(c.left(0x00000000UL)==60000UL-4096UL);
  c.pauseOrResume(0x00000000UL);assert(!c.running && c.left(900)==60000UL-4096UL);
  c.pauseOrResume(0x00000000UL);
  assert(!c.tick(30000UL));assert(c.running);
  assert(c.tick(61000UL));assert(c.finished && !c.running && c.left(62000)==0);
  assert(!c.tick(63000UL));
  c.pauseOrResume(64000UL);assert(!c.finished && c.running);
  c.reset();assert(c.left(70000UL)==60000 && !c.finished);
  c.chooseMinutes(0);assert(c.minutes==90);
  c.chooseMinutes(91);assert(c.minutes==1);
  jjk::Stopwatch w;
  w.pauseOrResume(1000);assert(w.elapsed(9000)==8000);
  w.pauseOrResume(9000);assert(!w.running && w.elapsed(60000)==8000);
  w.pauseOrResume(100000);assert(w.elapsed(101000)==9000);
  w.reset();assert(w.elapsed(101000)==0);
  std::cout<<"JJK timer and stopwatch rollover/pause tests PASS\n";
}
