#pragma once
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <ctime>
#include <sys/time.h>
#include <algorithm>
using std::uint8_t;
using std::uint16_t;
using std::uint32_t;
class String {
  std::string s;
 public:
  String()=default;String(const char* p):s(p?p:""){};
  String(std::string p):s(std::move(p)){};
  String(int n):s(std::to_string(n)){};
  String(unsigned n):s(std::to_string(n)){};
  size_t length()const{return s.size();}
  char operator[](unsigned i) const {return s[i];}
  long toInt() const{return std::strtol(s.c_str(),nullptr,10);}
  const char *c_str()const{return s.c_str();}
  void replace(const char *a,const char *b){size_t at=0;while((at=s.find(a,at))!=s.npos){s.replace(at,strlen(a),b);at+=strlen(b);}}
  String substring(unsigned a)const{return a<s.size()?s.substr(a):"";}
  String substring(unsigned a,unsigned b)const{return a<s.size()?s.substr(a,b-a):"";}
  bool equals(const String& o)const{return s==o.s;}
  void toCharArray(char *p,size_t n)const{if(n){std::strncpy(p,s.c_str(),n-1);p[n-1]=0;}}
  String operator+(const String& v)const{return s+v.s;}
  String& operator+=(const String& v){s+=v.s;return *this;}
};
inline String operator+(const char*a,const String& b){return String(a)+b;}
struct FakeSerial {void begin(int){};};
extern FakeSerial Serial;
constexpr int INPUT=0,OUTPUT=1,INPUT_PULLUP=2,LOW=0,HIGH=1;
uint32_t millis();void delay(int);void delayMicroseconds(int);void digitalWrite(int,int);
void pinMode(int,int);int digitalRead(int);void tone(int,unsigned,unsigned);void noTone(int);
uint32_t esp_random();void configTzTime(const char*,const char*,const char*);
