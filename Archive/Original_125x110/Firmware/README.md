# JJK Alarm firmware

Open `JJK_Alarm/JJK_Alarm.ino` in Arduino IDE. The sketch folder and `.ino` basename match.

1. Install the ESP32 board package by Espressif and select **Seeed XIAO ESP32C3**.
2. Install **Adafruit GFX Library** and **Adafruit ST7735 and ST7789 Library**, including dependencies.
3. Copy `JJK_Alarm/secrets.example.h` to `JJK_Alarm/secrets.h`. Enter Wi-Fi credentials locally, or leave the SSID blank for manual clock setting. Use a unique portal PIN of at least six characters to enable phone editing. Never commit `secrets.h`.
4. Keep `JJK_BUZZER_VERIFIED` and `JJK_HARDWARE_INSPECTED` at **0** for first-power inspection. The committed configuration intentionally makes no buzzer sound. These flags are user attestations, not electrical protection.
5. Compile and upload through the XIAO USB-C connector. Use Serial Monitor at **115200 baud** for pin-map and key-event diagnostics.

## Hardware map

| Function | ESP32 GPIO |
| --- | ---: |
| TFT SCK | 21 |
| TFT MOSI | 20 |
| TFT DC | 3 |
| TFT CS | 4 |
| Key columns | 5, 6, 7 |
| LEFT / RIGHT rows | 8 / 9 |
| Q1 buzzer driver | 10 |

J3: 1 GND, 2 +3V3, 3 SCK, 4 MOSI, 5 RST/+3V3, 6 DC, 7 CS, 8 BL/GND. The physical display wiring must follow its printed labels. Reset and backlight are not firmware GPIO outputs on this PCB.

Display: `init(76,284)`, column offset 82, row offset 18, `invertDisplay(false)`, rotation 0. The supplied 76x76 hand-sign graphic is stored in flash. Hours and minutes appear vertically below it.

## Controls

UP/DOWN change menu values. TIME sets time/date and its long press opens status. CLOCK sets alarm/weekdays and its long press opens the countdown. SNOOZE delays a ringing alarm by five minutes; a long press dismisses it. ALARM toggles the alarm and its long press changes the accent. Hold DOWN at home for the stopwatch.

Wi-Fi synchronizes the system clock with NTP. Without Wi-Fi, time/date can be set manually. Settings persist in NVS; an unpowered board cannot keep time or ring. The local phone portal uses HTTP and is for a trusted private network only. Do not port-forward it.

## Code structure

- `JJK_Alarm.ino`: display, button scanning, alarm handling, UI, local portal.
- `BoardConfig.h`: pin map for the current rectangular board.
- `AlarmLogic.h`: weekday selection, clock helpers, and daily trigger logic.
- `TimeTools.h`: countdown and stopwatch.
- `JJK_Hands_76x76.h`: image palette and pixel data.
- `secrets.example.h`: blank credential template and first-power sound settings.

The canonical project name is **JJK Alarm**, including the configuration macros, local phone hostname (`jjk-alarm.local`), and settings namespace. If you previously flashed older development firmware, re-enter settings previously stored under the old NVS namespace.

Compilation and host tests have passed. No physical alarm, TFT, button, or overnight operation test is claimed by those software results. The timer is visual-only in this build. The backlight is hard-wired on and deep sleep is not implemented.

This firmware has substantial AI assistance, disclosed in the project README. Program acceptance is a reviewer decision.
