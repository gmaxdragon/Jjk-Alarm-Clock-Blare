#pragma once
/* GGK Alarm Rev C physical KiCad net map. GPIO values, NOT Seeed D labels.

   Seeed XIAO ESP32-C3: D1=GPIO3, D2=GPIO4, D3=GPIO5,
   D4=GPIO6, D5=GPIO7, D6=GPIO21, D7=GPIO20, D8=GPIO8,
   D9=GPIO9, D10=GPIO10.  D0=GPIO2 is deliberately unused.

   Key scanner: D8/D9 are high-impedance INPUT_PULLUP ROWS.
   The column outputs D3/D4/D5 go LOW one at a time, never HIGH.
   1N4148 CATHODES/BARS connect towards switch/K1..K6, ANODES to rows.
   Boot strap D9 remains input and the XIAO's own pull-up holds it high.
   Never ground ROW_D9 on power-up or during flashing.

   TFT 8-pin kit screen is off-board via 8 F-F wires:
   J1.1 GND, 2 3V3, 3 SCL/SCK (D6), 4 SDA/MOSI (D7),
   5 RST 3V3, 6 DC (D1), 7 CS (D2), 8 BL GND.
   TFT BL tied to ground = backlight physically ALWAYS ON. A black screen
   does NOT equal low-power. Do not claim battery-friendly dark sleep.

   Buzzer pin GPIO10 (D10): default software policy forbids sounding it
   until the exact kit part has been checked for GPIO-safe current and type.
   Direct GPIO is allowed only for a VERIFIED low-current passive piezo.
   Active electromagnetic buzzer requires a transistor/driver re-design.
*/
#include <stdint.h>
namespace ggkpin {
constexpr uint8_t TFT_SCK = 21, TFT_MOSI = 20, TFT_DC = 3, TFT_CS = 4;
constexpr uint8_t BUZZER = 10;
constexpr uint8_t ROW0 = 8, ROW1 = 9;
constexpr uint8_t COL0 = 5, COL1 = 6, COL2 = 7;
}
