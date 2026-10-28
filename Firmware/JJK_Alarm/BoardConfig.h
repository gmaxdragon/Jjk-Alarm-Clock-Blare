#pragma once
// BLARE rectangular PCB (125 x 110 mm) / Seeed XIAO ESP32-C3.
// These numbers are CHIP GPIOs, not D labels.
//
// J1/J2 are two 7-way headers/sockets carrying ONE XIAO.
// Seeed pin map:
// D1=GPIO3, D2=GPIO4, D3=GPIO5, D4=GPIO6, D5=GPIO7,
// D6=GPIO21, D7=GPIO20, D8=GPIO8, D9=GPIO9, D10=GPIO10.
// D0/GPIO2, J2.1 VBUS unused.
//
// J3 8-way TFT male header; off-board 76 x 284 ST7789 on provided wires:
// 1=GND 2=3V3 3=SCL(GPIO21) 4=SDA(GPIO20) 5=RST(3V3)
// 6=DC(GPIO3) 7=CS(GPIO4) 8=BL(GND, active LOW).
// The panel is physically PORTRAIT. 284 x 76 is landscape, not this case.
//
// Keyboard: 3 columns x 2 rows (SW1..6 arranged as one horizontal strip).
// SW1 UP: COL_TOP+LEFT; SW2 DOWN: COL_TOP+RIGHT.
// SW3 TIME: COL_MID+LEFT; SW4 CLOCK: COL_MID+RIGHT.
// SW5 SNOOZE: COL_BOT+LEFT; SW6 ALARM: COL_BOT+RIGHT.
// LEFT(GPIO8) has an external 10k 3V3 pull-up; RIGHT(GPIO9) has the
// XIAO's BOOT pull-up. Diode BAR/cathode faces each switch.
// Columns default Hi-Z and only ever drive LOW during matrix scans.
// Never force GPIO8 and GPIO9 both LOW while entering bootloader mode.
//
// BZ1 low-side buzzer: +3V3 -> BZ1(+) -> BZ1(-) -> Q1 collector;
// Q1 emitter GND; GPIO10 through R2=1k into base, R3=100k base-to-GND.
// D7 is an OPTIONAL clamp across BZ1, cathode at +3V3.
// Q1 isolates load current from ESP32; it does NOT validate buzzer type.
// Sound stays OFF by default until part current/polarity and wiring verified.
//
// No LiPo installed. USB-C provides 5V via the XIAO; BL is hard-wired
// on, so deep sleep will not shut down the display backlight.
#include <stdint.h>
namespace jjkpin {
constexpr uint8_t TFT_SCK=21, TFT_MOSI=20, TFT_DC=3, TFT_CS=4;
constexpr uint8_t BUZZER=10;
constexpr uint8_t ROW0=8, ROW1=9;
constexpr uint8_t COL0=5, COL1=6, COL2=7;
}
