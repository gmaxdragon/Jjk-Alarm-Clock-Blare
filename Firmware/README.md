# GGK Alarm Rev D firmware

Arduino IDE board: **Seeed XIAO ESP32C3** (ESP32 by Espressif); libraries:
**Adafruit GFX**, **Adafruit ST7735 and ST7789**. Uses built-in `WiFi`, `WebServer`,
`ESPmDNS`, and `Preferences` on ESP32 Arduino core.

1. Copy `GGK_Alarm/secrets.example.h` to `GGK_Alarm/secrets.h` locally.
2. Add a private Wi-Fi SSID/password and unique local PIN (at least six chars).
3. KEEP `GGK_BUZZER_VERIFIED 0` and `GGK_HARDWARE_INSPECTED 0` until the exact kit buzzer and soldering have been physically checked and tested.
4. Flash via the XIAO's USB-C port. The board has **no built-in battery**. A stable external USB power bank is an alternative to wall power; not all power banks maintain power overnight.
5. Visit `http://ggk-alarm.local/` or the device's IP from your phone on the same trusted Wi-Fi network. PIN required to modify settings or sync time.

## Physical buttons (single row, left-to-right)

| Position | Function |
| --- | --- |
| 1 | UP / move selection upward |
| 2 | DOWN / move selection downward |
| 3 | TIME SET: clock time/date editor; hold for info/status |
| 4 | CLOCK SET: set alarm time and weekdays; confirm GGK quiz answer |
| 5 | SNOOZE: during alarm, wait five minutes; hold to skip/dismiss |
| 6 | ALARM ON: toggle enabled; hold for UI color theme; toggle alarm weekday when editing |

Time editor steps: hour → minute → month → date → year → save. Use UP/DOWN to change each.
Clock/alarm editor steps: hour → minute → selected weekdays → save.
The alarm defaults to **disabled** for safety until the user configures it.

## Display

The BLARE ST7789 is a **76 x 284 pixel portrait display**, and cannot fit the entire
large `10:24 AM` string on a single row. Rev D shows hour and minute on separate
large rows and `AM` or `PM` below. You can customize the caption, date visibility,
and red/cyan/gold accents from the phone portal. The screen's hardware backlight
pin is grounded; a software black screen **cannot physically switch it off**.

## Important limitations

- **Real Arduino ESP32-C3 compilation passes in GitHub Actions**, including the Adafruit libraries; no hardware has been flashed or measured. Pin constants are aligned to KiCad, but actual TFT offsets, the piezo type, boot with pressed keys and physical assembly must still be verified.
- Kit includes no battery, battery connector, fuel gauge, physical RTC, or protection board. This does **not** run independently once every source of USB power is unplugged.
- Power loss interrupts the alarm; settings persist but manual time needs resetting unless NTP reconnects. Do not use as the only morning alarm until tested.
- The 3.3V piezo must NOT be operated until measured for low-current passive-piezo behavior; if active magnetic buzzer, a transistor driver with resistor and protection is needed.
- `GGK_BUZZER_VERIFIED` and `GGK_HARDWARE_INSPECTED` are user attestations, **not a hardware safety interlock**.
- Wi-Fi portal uses local plaintext HTTP with PIN; only use on trusted Wi-Fi. Never expose the site to the public Internet or open router port forwarding.
- Alarm auto-stops after 180 s to limit sustained sound/current. This sacrifices guaranteed wakefulness to limit unattended activation.

## Added kit-only timer and stopwatch

No extra parts: **hold CLOCK SET** on the clock face for a 1–90 minute countdown timer, or **hold DOWN** for a stopwatch. Use CLOCK SET to start/pause, SNOOZE to reset, and TIME SET to exit. Countdown completion is **visual only** while the supplied piezo remains electrically unverified. These features need power continuously; no standalone battery/RTC is included.

## Design verification vs use in a bedroom

GitHub CI produces an **electrical/software prototype design**. No battery protection, overcurrent fuse, independently verified TFT/buzzer or physical safety testing is included. A supervising adult must check soldering and power; do not leave untested DIY hardware on overnight. See `../Docs/SAFETY_FIRST_POWER.md` from the repository root.
