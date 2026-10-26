/*
 GGK ALARM Rev C -- BLARE XIAO ESP32-C3 + portrait ST7789 76x284.
 Editable phone settings, direct six-key control, persistent weekday alarm,
 manual time/date setting, NTP, optional 5-minute snooze and quiz.

 SECURITY/SAFETY:
 - Prototype firmware: not compiled/flashed against a physical XIAO yet.
 - "SAFE BUZZER" is DISABLED unless exact piezo/current and wiring verified.
 - No Li-ion circuit is designed here. USB-only or verified external power bank.
 - No false battery percent, fake dimming or claim of autonomous time retention.
 - ESP32 C3 GPIO9 boot-strap pin is strictly a pulled-up keyboard ROW INPUT.
 - Sleep/deep-sleep disabled. TFT active-low BL is physically held on by PCB.
 - All PIN-secured settings travel over local HTTP, not public Internet/TLS.
 - Standalone daily waking requires complete test + separately reliable backup.
*/
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <time.h>
#include <sys/time.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include "BoardConfig.h"
#include "AlarmLogic.h"
#include "TimeTools.h"
#include "secrets.h"

class TinyPortrait : public Adafruit_ST7789 {
 public:
  TinyPortrait() : Adafruit_ST7789(ggkpin::TFT_CS, ggkpin::TFT_DC,
                     ggkpin::TFT_MOSI, ggkpin::TFT_SCK, -1) {}
  void begin() {
    init(76, 284);
    _colstart = _colstart2 = 82;
    _rowstart = _rowstart2 = 18;
    invertDisplay(false);
    setRotation(0);                  // real physical portrait, not a mockup
    fillScreen(ST77XX_BLACK);
  }
};

TinyPortrait tft;
WebServer portal(80);
Preferences prefs;
ggk::Alarm configuredAlarm;
ggk::Countdown countdown;
ggk::Stopwatch stopwatch;

static constexpr uint8_t ROW[2] = {ggkpin::ROW0, ggkpin::ROW1};
static constexpr uint8_t COL[3] = {ggkpin::COL0, ggkpin::COL1, ggkpin::COL2};
enum Key : uint8_t { UP=0, DOWN=1, TIME_SET=2, CLOCK_SET=3, SNOOZE=4, ALARM_ON=5 };
enum class Event : uint8_t { NONE, SHORT, LONG };
enum class Mode : uint8_t { HOME, TIME_EDIT, ALARM_EDIT, DAY_EDIT, QUIZ, INFO, TIMER, STOPWATCH };
struct Debounce {
  bool raw=false, pressed=false, longSent=false;
  uint32_t changed=0, pressedAt=0;
};
Debounce buttons[6];
Mode mode=Mode::HOME;
uint8_t theme=0, timeField=0, alarmField=0, chosenDay=1, question=0, answer=0;
bool showDate=true;
char caption[12]="GGK ALARM";
struct tm editedTime {};
int lastAlarmDay=-1;
time_t snoozeUntil=0;
bool alerting=false;
uint32_t alertAtMs=0, lastPulseMs=0, lastPaintMs=0, lastWifiAttempt=0;
bool redraw=true, buzzerOn=false, portalStarted=false, ntpStarted=false;
const char* weekdays[]={"SUN","MON","TUE","WED","THU","FRI","SAT"};
const char* questions[]={"SUKUNA?", "DOMAIN?", "SERIES?"};
const char* choices[3][3]={
  {"10", "20", "30"},
  {"INFINITE", "CHIMERA", "MALEVOLENT"},
  {"JUJUTSU", "NARUTO", "BLEACH"}
};

bool soundAllowed(){return GGK_BUZZER_VERIFIED==1 && GGK_HARDWARE_INSPECTED==1;}
uint16_t colorAccent(){return theme==1?0x07FF:theme==2?0xFFE0:0xF800;}
uint32_t currentMs(){return millis();}
int stringToInt(const String& s,int lo,int hi,int fallback){
  if(s.length()==0 || s.length()>8)return fallback;
  for(unsigned i=0;i<s.length();i++)if(s[i]<'0'||s[i]>'9')return fallback;
  int v=s.toInt();return v>=lo&&v<=hi?v:fallback;
}
void remember(){
  prefs.putUChar("hh",configuredAlarm.hour);prefs.putUChar("mm",configuredAlarm.minute);
  prefs.putUChar("days",configuredAlarm.days);prefs.putBool("on",configuredAlarm.enabled);
  prefs.putUChar("theme",theme);prefs.putBool("date",showDate);
  prefs.putString("caption",caption);
}
void loadSettings(){
  prefs.begin("ggk-alarm",false);
  configuredAlarm.hour=prefs.getUChar("hh",7);configuredAlarm.minute=prefs.getUChar("mm",0);
  configuredAlarm.days=prefs.getUChar("days",ggk::SCHOOL_DAYS);
  configuredAlarm.enabled=prefs.getBool("on",false);
  theme=prefs.getUChar("theme",0)%3;
  showDate=prefs.getBool("date",true);
  String label=prefs.getString("caption","GGK ALARM");
  if(!ggk::validLabel(label.c_str()))label="GGK ALARM";
  label.toCharArray(caption,sizeof(caption));
  lastAlarmDay=prefs.getInt("lastday",-1);
  if(!ggk::valid(configuredAlarm))configuredAlarm=ggk::Alarm{};
}

// The PCB diode cathode/bar is K1..K6 (on the switch side), while anode
// faces the ROW bus. ROW pull-up -> diode -> pressed switch -> LOW COLUMN.
uint8_t scanPressed(){
  uint8_t mask=0;
  for(int c=0;c<3;c++){
    digitalWrite(COL[c],LOW);
    pinMode(COL[c],OUTPUT);        // drive only LOW, never source into a short
    delayMicroseconds(80);
    for(int r=0;r<2;r++){
      int k=ggk::keyFromMatrix(c,r);
      if(digitalRead(ROW[r])==LOW)mask|=(uint8_t(1)<<k);
    }
    pinMode(COL[c],INPUT);          // high-Z between scanning windows
  }
  return mask;
}

void setBuzzerOff(){
  if(buzzerOn){noTone(ggkpin::BUZZER);buzzerOn=false;}
  digitalWrite(ggkpin::BUZZER,LOW);
}
void playVerifiedTone(unsigned frequency,unsigned duration){
  if(!soundAllowed())return;      // fail CLOSED on unknown buzzer type
  if(duration>280)duration=280;
  tone(ggkpin::BUZZER,frequency,duration);
  buzzerOn=true;
}
void dismiss(){
  setBuzzerOff();alerting=false;snoozeUntil=0;
  mode=Mode::HOME;redraw=true;
}
void snooze(){
  setBuzzerOff();alerting=false;
  time_t now=time(nullptr);
  if(now>1700000000)snoozeUntil=now+ggk::SNOOZE_SECONDS;
  else snoozeUntil=0;
  mode=Mode::HOME;redraw=true;
}
void startAlert(){
  alerting=true;snoozeUntil=0;alertAtMs=currentMs();lastPulseMs=0;
  question=(uint8_t)(esp_random()%3);answer=0;
  mode=Mode::QUIZ;redraw=true;
}

// Returns false if date/time has not been synchronized or manually set.
bool localNow(tm& t){
  time_t now=time(nullptr);
  if(now<1700000000)return false;
  return localtime_r(&now,&t)!=nullptr;
}
void checkAlarm(){
  struct tm t{};
  if(!localNow(t))return;
  time_t now=time(nullptr);
  if(snoozeUntil && now>=snoozeUntil){startAlert();return;}
  if(snoozeUntil || alerting)return;
  ggk::Clock c{t.tm_year+1900,t.tm_yday,t.tm_wday,t.tm_hour,t.tm_min};
  if(ggk::due(configuredAlarm,c,lastAlarmDay)){
    lastAlarmDay=ggk::dateKey(c);
    prefs.putInt("lastday",lastAlarmDay);  // once/day NVS write
    startAlert();
  }
}
void serviceAlarmSound(){
  if(!alerting){setBuzzerOff();return;}
  uint32_t elapsed=currentMs()-alertAtMs;
  if(elapsed>ggk::MAX_RING_SECONDS*1000UL){dismiss();return;}
  if(!soundAllowed())return;
  // Beep spacing increases perceived urgency without overdriving the buzzer.
  // Maximum pulse width 250 ms; no all-night continuous drive.
  const uint16_t notes[]={392,466,523,622,784,932};
  uint32_t period=elapsed<30000?1300:elapsed<90000?950:700;
  if(lastPulseMs==0 || currentMs()-lastPulseMs>=period){
    lastPulseMs=currentMs();
    playVerifiedTone(notes[(elapsed/period)%6],
                     elapsed<30000?130:elapsed<90000?180:250);
  }
}

// ---- User-interface primitives on the *real* 76 x 284 portrait display ----
void small(const char* s,int x,int y,uint16_t color){
  tft.setTextWrap(false);tft.setTextSize(1);tft.setTextColor(color);
  tft.setCursor(x,y);tft.print(s);
}
void banner(const char* s){
  tft.fillScreen(ST77XX_BLACK);
  small(s,4,7,colorAccent());
  tft.drawFastHLine(3,20,70,colorAccent());
}
void twoDigits(int value,int x,int y){
  char b[8];snprintf(b,sizeof(b),"%02d",value);
  tft.setTextSize(4);tft.setTextColor(ST77XX_WHITE);
  tft.setCursor(x,y);tft.print(b);
}
void centered(int value,int y){twoDigits(value,14,y);}
void paintHome(){
  struct tm t{};bool validTime=localNow(t);
  banner(caption);
  if(!validTime){
    small("NO TIME",8,53,ST77XX_WHITE);
    small("TIME SET",8,79,colorAccent());
    small("OR WIFI",8,95,ST77XX_WHITE);
  }else{
    centered(ggk::hour12(t.tm_hour),45);
    tft.drawFastHLine(10,95,56,colorAccent());
    centered(t.tm_min,104);
    small(ggk::period(t.tm_hour),29,154,ST77XX_WHITE);
    if(showDate){
      char day[12];snprintf(day,sizeof(day),"%s %02d/%02d",weekdays[t.tm_wday],t.tm_mon+1,t.tm_mday);
      small(day,3,182,ST77XX_WHITE);
    }
  }
  small(configuredAlarm.enabled?"ALARM ON":"ALARM OFF",5,216,colorAccent());
  char next[12];snprintf(next,sizeof(next),"%02d:%02d %s",ggk::hour12(configuredAlarm.hour),configuredAlarm.minute,ggk::period(configuredAlarm.hour));
  small(next,5,232,ST77XX_WHITE);
  if(snoozeUntil)small("SNOOZE 5M",5,247,colorAccent());
  if(!soundAllowed())small("AUDIO HOLD",5,260,0xFBE0);
  else small("SOUND READY",5,260,0x07E0);
}
void paintEdit(){
  bool timeMode=mode==Mode::TIME_EDIT;
  const char* fields[]={"SET HOUR","SET MIN","SET MONTH","SET DAY","SET YEAR"};
  banner(timeMode?"TIME SET":"CLOCK SET");
  int value=0;const char* name="";
  if(timeMode){
    name=fields[timeField];
    if(timeField==0)value=editedTime.tm_hour;
    if(timeField==1)value=editedTime.tm_min;
    if(timeField==2)value=editedTime.tm_mon+1;
    if(timeField==3)value=editedTime.tm_mday;
    if(timeField==4)value=editedTime.tm_year+1900;
  }else{
    name=alarmField==0?"ALARM HOUR":"ALARM MIN";
    value=alarmField==0?configuredAlarm.hour:configuredAlarm.minute;
  }
  small(name,4,44,colorAccent());
  if(value>=100){
    char b[8];snprintf(b,sizeof(b),"%04d",value);
    small(b,13,107,ST77XX_WHITE);
  }else centered(value,95);
  small("UP / DOWN",4,167,ST77XX_WHITE);
  small(timeMode?"TIME: NEXT":"CLOCK:NEXT",4,194,colorAccent());
  small("SNOOZE:EXIT",4,243,ST77XX_WHITE);
}
void paintDays(){
  banner("PICK DAYS");
  for(int i=0;i<7;i++){
    int y=35+i*27;
    bool selected=ggk::chosen(configuredAlarm,i);
    if(i==chosenDay)tft.fillRect(0,y-4,76,23,colorAccent());
    small(weekdays[i],4,y,i==chosenDay?ST77XX_BLACK:ST77XX_WHITE);
    small(selected?"ON":"--",43,y,i==chosenDay?ST77XX_BLACK:ST77XX_WHITE);
  }
  small("ALARM:FLIP",4,231,colorAccent());
  small("CLOCK:SAVE",4,247,ST77XX_WHITE);
}
void paintQuiz(){
  banner("WAKE UP!");
  small(questions[question],4,45,colorAccent());
  for(int i=0;i<3;i++){
    int y=83+i*39;
    if(i==answer)tft.fillRect(0,y-4,76,31,colorAccent());
    const char* a=choices[question][i];
    char b[13];strncpy(b,a,12);b[12]=0;
    small(b,3,y,i==answer?ST77XX_BLACK:ST77XX_WHITE);
  }
  small("CLOCK:OK",4,218,ST77XX_WHITE);
  small("SNOOZE:5M",4,241,colorAccent());
  small("HOLD SNOOZE",4,257,ST77XX_WHITE);
}
void paintInfo(){
  banner("STATUS");
  small(WiFi.status()==WL_CONNECTED?"WIFI:OK":"WIFI:OFF",4,42,ST77XX_WHITE);
  if(WiFi.status()==WL_CONNECTED){
    String ip=WiFi.localIP().toString();
    // On a 76px-wide portrait TFT, split IPv4 into 2 lines.
    small(ip.substring(0,12).c_str(),1,68,colorAccent());
    if(ip.length()>12)small(ip.substring(12).c_str(),1,83,colorAccent());
  }
  small(soundAllowed()?"BUZ:READY":"BUZ:LOCK",3,126,ST77XX_WHITE);
  small("USB / BANK",3,149,ST77XX_WHITE);
  small("NO INTERNAL",3,166,ST77XX_WHITE);
  small("BATTERY",3,181,ST77XX_WHITE);
  small("TIME:BACK",3,252,colorAccent());
}
void paintTimer(){
  banner("COUNTDOWN");
  const uint32_t left=countdown.left(currentMs());
  const unsigned secs=(left+999U)/1000U;
  char value[12];snprintf(value,sizeof(value),"%02u:%02u",
      (unsigned)(secs/60),(unsigned)(secs%60));
  tft.setTextColor(ST77XX_WHITE);tft.setTextSize(2);tft.setCursor(8,85);tft.print(value);
  small(countdown.finished?"TIMER DONE":countdown.running?"RUNNING":"PAUSED",4,143,colorAccent());
  small("UP/DOWN MINS",3,176,ST77XX_WHITE);
  small("CLOCK:GO/PAUS",3,207,colorAccent());
  small("SNOOZE:RESET",3,232,ST77XX_WHITE);
  small("TIME:EXIT",3,254,ST77XX_WHITE);
}
void paintStopwatch(){
  banner("STOPWATCH");
  uint32_t seconds=stopwatch.elapsed(currentMs())/1000UL;
  char value[13];snprintf(value,sizeof(value),"%02u:%02u",
      (unsigned)((seconds/60)%100),(unsigned)(seconds%60));
  tft.setTextColor(ST77XX_WHITE);tft.setTextSize(2);tft.setCursor(8,85);tft.print(value);
  small(stopwatch.running?"RUNNING":"PAUSED",4,145,colorAccent());
  small("CLOCK:GO/PAUS",3,207,ST77XX_WHITE);
  small("SNOOZE:RESET",3,232,ST77XX_WHITE);
  small("TIME:EXIT",3,254,ST77XX_WHITE);
}
void paint(){
  switch(mode){
    case Mode::HOME:paintHome();break;
    case Mode::TIME_EDIT:case Mode::ALARM_EDIT:paintEdit();break;
    case Mode::DAY_EDIT:paintDays();break;
    case Mode::QUIZ:paintQuiz();break;
    case Mode::INFO:paintInfo();break;
    case Mode::TIMER:paintTimer();break;
    case Mode::STOPWATCH:paintStopwatch();break;
  }
  lastPaintMs=currentMs();redraw=false;
}

void beginTimeEdit(){
  time_t t=time(nullptr);
  if(t>1700000000)localtime_r(&t,&editedTime);
  else{
    memset(&editedTime,0,sizeof(editedTime));
    editedTime.tm_year=126;editedTime.tm_mon=0;editedTime.tm_mday=1;
    editedTime.tm_hour=7;editedTime.tm_min=0;
  }
  timeField=0;mode=Mode::TIME_EDIT;redraw=true;
}
void adjustManual(int delta){
  switch(timeField){
    case 0:editedTime.tm_hour=ggk::wrap(editedTime.tm_hour+delta,24);break;
    case 1:editedTime.tm_min=ggk::wrap(editedTime.tm_min+delta,60);break;
    case 2:editedTime.tm_mon=ggk::wrap(editedTime.tm_mon+delta,12);break;
    case 3:editedTime.tm_mday=ggk::wrap(editedTime.tm_mday-1+delta,31)+1;break;
    case 4:editedTime.tm_year=ggk::wrap(editedTime.tm_year-124+delta,76)+124;break;
  }
}
void saveManualTime(){
  editedTime.tm_sec=0;editedTime.tm_isdst=-1;
  time_t stamp=mktime(&editedTime);
  if(stamp>=1700000000){timeval tv{stamp,0};settimeofday(&tv,nullptr);}
  mode=Mode::HOME;redraw=true;
}
void adjustAlarm(int delta){
  if(alarmField==0)configuredAlarm.hour=(uint8_t)ggk::wrap(int(configuredAlarm.hour)+delta,24);
  else configuredAlarm.minute=(uint8_t)ggk::wrap(int(configuredAlarm.minute)+delta,60);
}
void onKey(Key key,Event event){
  if(event==Event::NONE)return;
  if(alerting){
    if(key==SNOOZE){if(event==Event::LONG)dismiss();else snooze();return;}
    if(event==Event::LONG)return;
    if(key==UP)answer=(uint8_t)ggk::wrap(int(answer)-1,3);
    if(key==DOWN)answer=(uint8_t)ggk::wrap(int(answer)+1,3);
    if(key==CLOCK_SET && ggk::quizCorrect(question,answer))dismiss();
    redraw=true;return;
  }
  if(mode==Mode::TIMER){
    if(event==Event::SHORT){
      if(key==UP)countdown.chooseMinutes(int(countdown.minutes)+1);
      if(key==DOWN)countdown.chooseMinutes(int(countdown.minutes)-1);
      if(key==CLOCK_SET)countdown.pauseOrResume(currentMs());
      if(key==SNOOZE)countdown.reset();
      if(key==TIME_SET)mode=Mode::HOME;
    }
    redraw=true;return;
  }
  if(mode==Mode::STOPWATCH){
    if(event==Event::SHORT){
      if(key==CLOCK_SET)stopwatch.pauseOrResume(currentMs());
      if(key==SNOOZE)stopwatch.reset();
      if(key==TIME_SET)mode=Mode::HOME;
    }
    redraw=true;return;
  }
  if(mode==Mode::TIME_EDIT){
    if(event==Event::SHORT){
      if(key==UP)adjustManual(1);
      if(key==DOWN)adjustManual(-1);
      if(key==SNOOZE)mode=Mode::HOME;
      if(key==TIME_SET){if(++timeField>=5)saveManualTime();}
    }
    redraw=true;return;
  }
  if(mode==Mode::ALARM_EDIT){
    if(event==Event::SHORT){
      if(key==UP)adjustAlarm(1);
      if(key==DOWN)adjustAlarm(-1);
      if(key==SNOOZE)mode=Mode::HOME;
      if(key==CLOCK_SET){if(++alarmField>=2)mode=Mode::DAY_EDIT;}
    }
    redraw=true;return;
  }
  if(mode==Mode::DAY_EDIT){
    if(event==Event::SHORT){
      if(key==UP)chosenDay=(uint8_t)ggk::wrap(int(chosenDay)-1,7);
      if(key==DOWN)chosenDay=(uint8_t)ggk::wrap(int(chosenDay)+1,7);
      if(key==ALARM_ON)configuredAlarm.days ^= (uint8_t(1)<<chosenDay);
      if(key==CLOCK_SET){remember();mode=Mode::HOME;}
      if(key==SNOOZE)mode=Mode::HOME;
    }
    redraw=true;return;
  }
  if(mode==Mode::INFO){
    if(event==Event::SHORT && (key==TIME_SET||key==SNOOZE))mode=Mode::HOME;
    redraw=true;return;
  }
  if(mode==Mode::HOME){
    if(key==CLOCK_SET && event==Event::LONG){mode=Mode::TIMER;}
    else if(key==DOWN && event==Event::LONG){mode=Mode::STOPWATCH;}
    else if(key==TIME_SET && event==Event::LONG){mode=Mode::INFO;}
    else if(key==TIME_SET && event==Event::SHORT){beginTimeEdit();}
    else if(key==CLOCK_SET && event==Event::SHORT){
      alarmField=0;mode=Mode::ALARM_EDIT;
    }else if(key==ALARM_ON && event==Event::LONG){
      theme=(theme+1)%3;remember();
    }else if(key==ALARM_ON && event==Event::SHORT){
      configuredAlarm.enabled=!configuredAlarm.enabled;remember();
    }
    redraw=true;
  }
}

void pollKeys(){
  uint8_t mask=scanPressed();
  uint32_t now=currentMs();
  for(int i=0;i<6;i++){
    Debounce &b=buttons[i];bool v=((mask>>i)&1)!=0;
    if(v!=b.raw){b.raw=v;b.changed=now;}
    if(v!=b.pressed && now-b.changed>=35){
      b.pressed=v;
      if(v){b.pressedAt=now;b.longSent=false;}
      else if(!b.longSent){onKey((Key)i,Event::SHORT);}
    }
    if(b.pressed && !b.longSent && now-b.pressedAt>=1200){
      b.longSent=true;onKey((Key)i,Event::LONG);
    }
  }
}

// ----- Minimal local phone portal. Local HTTP only, password/PIN required.
String htmlEscape(String s){
  s.replace("&","&amp;");s.replace("<","&lt;");
  s.replace(">","&gt;");s.replace("\"","&quot;");
  return s;
}
bool portalReady(){return strlen(GGK_PORTAL_PIN)>=6;}
void renderPortal(){
  String html="<!doctype html><html><meta name='viewport' content='width=device-width,initial-scale=1'>";
  html+="<title>GGK Alarm</title><style>body{background:#0e1015;color:#f9f9f9;font-family:system-ui;margin:auto;max-width:460px;padding:24px}input,select,button{font:inherit;background:#242630;color:white;border:1px solid #52535b;border-radius:8px;padding:11px;margin:5px 0;width:100%;box-sizing:border-box}button{background:#9d2036}label{display:block;margin-top:13px}h1{color:#ff5265}</style>";
  html+="<h1>GGK ALARM</h1><p>Local Wi-Fi only. Physical keyboard always works.</p>";
  if(!portalReady())html+="<p>Phone editing locked until a unique portal PIN is set during flashing.</p>";
  else{
    html+="<form action='/save' method='POST'><label>Portal PIN<input type='password' name='pin' required></label>";
    html+="<label>Alarm hour (0-23)<input name='h' type='number' min='0' max='23' value='"+String(configuredAlarm.hour)+"'></label>";
    html+="<label>Alarm minute<input name='m' type='number' min='0' max='59' value='"+String(configuredAlarm.minute)+"'></label>";
    html+="<label>Weekday bits SUN=1 MON=2 TUE=4 WED=8 THU=16 FRI=32 SAT=64<input name='d' type='number' min='0' max='127' value='"+String(configuredAlarm.days)+"'></label>";
    html+="<label>Alarm on? (0/1)<input name='on' type='number' min='0' max='1' value='"+String(configuredAlarm.enabled?1:0)+"'></label>";
    html+="<label>Screen accent: 0=Red, 1=Cyan, 2=Gold<input name='theme' type='number' min='0' max='2' value='"+String(theme)+"'></label>";
    html+="<label>Display title (max 11 letters)<input name='label' maxlength='11' value='"+htmlEscape(String(caption))+"'></label>";
    html+="<label>Show date? (0/1)<input name='date' type='number' min='0' max='1' value='"+String(showDate?1:0)+"'></label>";
    html+="<button type='submit'>Save GGK settings</button></form>";
    html+="<hr><p>Sync clock from this phone:</p><label>Portal PIN<input id='syncPin' type='password'></label><button onclick='syncClock()'>Sync phone time</button><p id='syncResult'></p>";
    html+="<script>async function syncClock(){let data=new URLSearchParams({pin:document.getElementById('syncPin').value,unix:String(Math.floor(Date.now()/1000))});try{let r=await fetch('/sync',{method:'POST',body:data});document.getElementById('syncResult').textContent=await r.text()}catch(e){document.getElementById('syncResult').textContent='Sync failed'}}</script>";
  }
  html+="<p>Do not rely on this prototype as your only morning alarm until fully verified.</p></html>";
  portal.send(200,"text/html; charset=utf-8",html);
}
bool authorized(){
  return portalReady() && portal.hasArg("pin") &&
         portal.arg("pin").equals(String(GGK_PORTAL_PIN));
}
void saveViaPortal(){
  if(!authorized()){portal.send(403,"text/plain","PIN required or incorrect");return;}
  if(!portal.hasArg("h") || !portal.hasArg("m") || !portal.hasArg("d") ||
     !portal.hasArg("theme") || !portal.hasArg("on") || !portal.hasArg("label") || !portal.hasArg("date")){
    portal.send(400,"text/plain","Missing settings");return;
  }
  auto validNumber=[](const String& s,int lo,int hi){
    if(s.length()==0 || s.length()>3)return false;
    for(unsigned i=0;i<s.length();i++)if(s[i]<'0'||s[i]>'9')return false;
    return s.toInt()>=lo && s.toInt()<=hi;
  };
  if(!validNumber(portal.arg("h"),0,23) || !validNumber(portal.arg("m"),0,59) ||
     !validNumber(portal.arg("d"),0,127) || !validNumber(portal.arg("theme"),0,2) ||
     !validNumber(portal.arg("on"),0,1) || !validNumber(portal.arg("date"),0,1) ||
     !ggk::validLabel(portal.arg("label").c_str())){
    portal.send(422,"text/plain","Invalid settings; no changes saved");return;
  }
  configuredAlarm.hour=(uint8_t)portal.arg("h").toInt();
  configuredAlarm.minute=(uint8_t)portal.arg("m").toInt();
  configuredAlarm.days=(uint8_t)portal.arg("d").toInt();
  configuredAlarm.enabled=portal.arg("on").toInt()==1;
  theme=(uint8_t)portal.arg("theme").toInt();
  showDate=portal.arg("date").toInt()==1;
  portal.arg("label").toCharArray(caption,sizeof(caption));
  remember();redraw=true;
  portal.sendHeader("Location","/",true);portal.send(303,"text/plain","Saved");
}
void syncViaPortal(){
  if(!authorized()){portal.send(403,"text/plain","PIN required or incorrect");return;}
  String val=portal.arg("unix");
  if(val.length()!=10){portal.send(422,"text/plain","Invalid phone timestamp");return;}
  for(unsigned i=0;i<val.length();i++)if(val[i]<'0'||val[i]>'9'){
    portal.send(422,"text/plain","Invalid time input");return;
  }
  uint64_t n=strtoull(val.c_str(),nullptr,10);
  if(n<1700000000ULL || n>4102444799ULL){
    portal.send(422,"text/plain","Date is out of range");return;
  }
  timeval t{(time_t)n,0};settimeofday(&t,nullptr);redraw=true;
  portal.send(200,"text/plain","Phone time synchronized");
}
void preparePortal(){
  portal.on("/",HTTP_GET,renderPortal);
  portal.on("/save",HTTP_POST,saveViaPortal);
  portal.on("/sync",HTTP_POST,syncViaPortal);
  portal.onNotFound([]{portal.send(404,"text/plain","Unknown GGK route");});
  portal.begin();portalStarted=true;
  MDNS.begin("ggk-alarm");
}
void serviceWifi(){
  if(strlen(GGK_WIFI_SSID)==0)return;
  if(WiFi.status()==WL_CONNECTED){
    if(!portalStarted)preparePortal();
    if(!ntpStarted){
      configTzTime(GGK_TIMEZONE,"pool.ntp.org","time.google.com");
      ntpStarted=true;
    }
    return;
  }
  if(currentMs()-lastWifiAttempt>45000UL){
    lastWifiAttempt=currentMs();WiFi.disconnect();
    WiFi.begin(GGK_WIFI_SSID,GGK_WIFI_PASSWORD);
  }
}

void setup(){
  Serial.begin(115200);
  digitalWrite(ggkpin::BUZZER,LOW);
  pinMode(ggkpin::BUZZER,OUTPUT);
  setBuzzerOff();
  for(int i=0;i<2;i++)pinMode(ROW[i],INPUT_PULLUP);
  for(int i=0;i<3;i++){digitalWrite(COL[i],LOW);pinMode(COL[i],INPUT);}
  setenv("TZ",GGK_TIMEZONE,1);tzset();
  loadSettings();
  tft.begin();
  if(strlen(GGK_WIFI_SSID)){
    WiFi.mode(WIFI_STA);WiFi.setAutoReconnect(true);
    WiFi.begin(GGK_WIFI_SSID,GGK_WIFI_PASSWORD);
    lastWifiAttempt=currentMs();
  }else WiFi.mode(WIFI_OFF);
  paint();
}
void loop(){
  pollKeys();
  serviceWifi();
  if(portalStarted)portal.handleClient();
  checkAlarm();serviceAlarmSound();
  if(countdown.tick(currentMs()))redraw=true; // visual timer; no unverified buzzer drive
  if(redraw || currentMs()-lastPaintMs>1000)paint();
  delay(10);
}
