#include "../Firmware/GGK_Alarm/AlarmLogic.h"
#include <cassert>
#include <cstring>
#include <iostream>
int main(){
 using namespace ggk;
 Alarm a; Clock t{2026,297,0,7,0};
 assert(valid(a)); assert(!a.enabled); assert(!due(a,t,-1));
 a.enabled=true; assert(!due(a,t,-1)); // Sunday disabled by default
 t.wday=1; assert(due(a,t,-1));
 assert(!due(a,t,dateKey(t))); // no same-day double alarm
 t.minute=1; assert(!due(a,t,-1));
 t.minute=0; t.hour=8; assert(!due(a,t,-1));
 a.hour=8; assert(due(a,t,-1));
 a.days=EVERY_DAY; t.wday=0; assert(due(a,t,-1));
 a.hour=24; assert(!valid(a));assert(!due(a,t,-1));
 a.hour=8; a.days=0x80; assert(!valid(a));
 assert(hour12(0)==12); assert(hour12(12)==12); assert(hour12(23)==11);
 assert(std::strcmp(period(0),"AM")==0); assert(std::strcmp(period(12),"PM")==0);
 assert(wrap(-1,60)==59);assert(wrap(60,60)==0);
 assert(keyFromMatrix(0,0)==0); assert(keyFromMatrix(0,1)==1);
 assert(keyFromMatrix(1,0)==2); assert(keyFromMatrix(1,1)==3);
 assert(keyFromMatrix(2,0)==4); assert(keyFromMatrix(2,1)==5);
 assert(keyFromMatrix(3,0)==-1);
 assert(quizCorrect(0,1));assert(!quizCorrect(0,0));
 assert(quizCorrect(1,2));assert(quizCorrect(2,0));
 assert(validLabel("GGK ALARM"));assert(validLabel(""));
 assert(!validLabel("THIS IS TOO LONG"));
 assert(SNOOZE_SECONDS==300 && MAX_RING_SECONDS==180);
 std::cout<<"GGK AlarmLogic: all 32 behavioral assertions PASS\n";
}
