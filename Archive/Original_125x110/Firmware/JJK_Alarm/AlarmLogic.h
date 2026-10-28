#pragma once
#include <stdint.h>
#include <stddef.h>
namespace jjk {
constexpr uint8_t SCHOOL_DAYS = 0x3E;
constexpr uint8_t EVERY_DAY = 0x7F;
constexpr unsigned SNOOZE_SECONDS = 300;
constexpr unsigned MAX_RING_SECONDS = 180; // fail-safe timeout, not a promise to wake anyone
struct Alarm {
  uint8_t hour = 7;
  uint8_t minute = 0;
  uint8_t days = SCHOOL_DAYS;
  bool enabled = false;  // fail-safe default: disabled until user sets it
};
struct Clock {
  int year = 0, yday = 0, wday = 0, hour = 0, minute = 0;
};
inline bool valid(const Alarm &a) {
  return a.hour < 24 && a.minute < 60 && (a.days & 0x80) == 0;
}
inline bool chosen(const Alarm &a, int weekday) {
  return weekday >= 0 && weekday <= 6 && ((a.days >> weekday) & 1);
}
inline int dateKey(const Clock &t) {return t.year*1000+t.yday;}
inline bool due(const Alarm &a, const Clock &t, int lastDay) {
  return valid(a) && a.enabled && chosen(a,t.wday) &&
         t.hour==a.hour && t.minute==a.minute && dateKey(t)!=lastDay;
}
inline int wrap(int x,int n) { return n>0 ? (x%n+n)%n : 0; }
inline int hour12(int h){return ((h+11)%12)+1;}
inline const char *period(int h){return h<12?"AM":"PM";}
inline bool quizCorrect(unsigned question,unsigned choice) {
  static constexpr unsigned correct[]={1,2,0};
  return question<3 && choice==correct[question];
}
// Exact matrix index: columns C0,C1,C2; rows R0,R1.
// SW1 UP, SW2 DOWN, SW3 TIME SET, SW4 CLOCK SET, SW5 SNOOZE, SW6 ALARM.
constexpr int keyFromMatrix(int col,int row) {
  return (col>=0&&col<3&&row>=0&&row<2)?(col*2+row):-1;
}
inline bool validLabel(const char *p) {
  if(!p)return false;
  unsigned n=0;
  while(*p) {
    if(++n>11)return false;
    const bool safe=(*p>='A'&&*p<='Z')||(*p>='a'&&*p<='z')||
      (*p>='0'&&*p<='9')||*p==' '||*p=='_'||*p=='-'||*p=='.';
    if(!safe)return false;
    p++;
  }
  return true;
}
}
