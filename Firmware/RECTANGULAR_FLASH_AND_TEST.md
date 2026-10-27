# BLARE rectangular PCB firmware bring-up (AI-assisted working build)

This technical file is NOT the submission README.

## Exact PCB pin map and display

- Controller: Seeed XIAO ESP32-C3 in the 2 x 7-pin J1/J2 sockets.
- TFT: J3 8-pin male header with provided F-F jumpers. J3 pin 1 GND,
  2 +3V3, 3 SCK GPIO21, 4 MOSI GPIO20, 5 RST +3V3,
  6 DC GPIO3, 7 CS GPIO4, 8 BL GND (active low).
- Physical portrait: width 76 pixels, height 284 pixels.
  In firmware: init(76,284), col offset 82, row offset 18,
  inversion false and rotation 0. The Hack Club example rotation 1
  is LANDSCAPE, not this physical portrait screen.
- Six switches from left: UP, DOWN, TIME, CLOCK, SNOOZE, ALARM.
  Three columns GPIO5/6/7; LEFT row GPIO8; RIGHT row GPIO9.
  1N4148 diode cathodes/bar on the individual switch side.
  R1 external 10k pull-up on GPIO8; GPIO9 held high by the XIAO BOOT circuit.
- BZ1 negative is switched by Q1 from GPIO10 through R2 1k,
  with R3 100k pulldown. D7 is an optional diode clamp.
  Software sound remains OFF until the real buzzer and circuit are verified.
- No internal battery, RTC, backlight switch or deep-sleep support.

## Flash and test

1. Install Arduino IDE and Espressif ESP32 board package. Select
   Seeed XIAO ESP32C3. Install Adafruit GFX and Adafruit ST7735/ST7789.
2. Copy secrets.example.h to secrets.h inside Firmware/GGK_Alarm.
   Add local Wi-Fi credentials or leave SSID empty for manual time.
   If using the phone portal choose a unique PIN. Never commit secrets.h.
3. KEEP GGK_BUZZER_VERIFIED 0 and GGK_HARDWARE_INSPECTED 0.
   Begin testing without a powered buzzer or TFT until 3V3 and GND
   and solder joints have been inspected.
4. Flash GGK_Alarm.ino over USB-C. Open Serial Monitor at 115200.
   It prints the pin map and audio gate status.
   With GGK_DEBUG_KEY_SERIAL 1 it logs each button press and hold.
5. Test all six keys, combinations and pressed-button boot behavior.
   The two row GPIOs must not prevent bootloader entry.
6. Attach TFT only after checking actual panel pin labels/voltage;
   verify 76x284 portrait and actual pixel offsets.
7. Set clock using NTP, phone portal, or TIME SET physical buttons.
   Check alarm enable, weekdays, snooze, AM/PM, timer and power cycle.
8. Sound stays silent until actual buzzer part/current and power
   switching are physically tested, including transistor pinout.
   Software flags do not prevent electrical overheating.
9. This is NOT approved as an unattended bedside alarm. No battery,
   no power-failure alarm and no tested physical alarm loudness.

## AI disclosure and shipping

The firmware was written/adapted with substantial ChatGPT AI assistance.
The user did the physical PCB/CAD work with guidance. Do NOT claim
the firmware or this note was wholly student-authored. Check Stardance
AI restrictions and write any required disclosure honestly. Reviewers
have returned submissions for excessive AI-generated code or README.

The shipping root README.md remains unchanged until user approval.
