# GGK Alarm — BLARE Rev D

**Design status: KiCad electrical validation passed; physical fabrication/overnight safety approval remains ON HOLD.** This is a custom GGK-themed bedside alarm clock built from the standard Hack Club BLARE electronics kit. **No extra electronic components or internal battery.**

## Hardware and design

- **Custom 99.3 × 99.3 mm T-shaped two-layer PCB** with a narrow display stalk and one six-switch horizontal keyboard bar. No artwork or key labels in the PCB silkscreen.
- **Six MX keyboard switches** wired as a 2-row × 3-column matrix using **six kit-supplied 1N4148 through-hole diodes**. LEFT TO RIGHT: Up, Down, Time Set, Clock Set, Snooze, Alarm On.
- **Seeed XIAO ESP32-C3** mounted on the back, USB-C accessible at the top. Its **22 edge/underside pad locations** were compared to the native KiCad board model.
- **Kit 2.25-inch ST7789 TFT display**, 76 × 284 pixels, oriented **portrait** and connected using the provided 8-pin header and jumper wires. Exact panel wiring/order and dimensions must be checked against the physically supplied module.
- **Kit 3.3 V piezo buzzer**, with output **disabled by default** in firmware until its current/type and GPIO compatibility are measured.
- **Only two top-stem M3 mounting holes** (H1, H2). The lower switch bar must be held by a properly designed printed case; don't assume the earlier four-hole Rev C drawing.

See `PCB/` for the **complete editable native KiCad project** and local embedded symbols/footprints, `Docs/Tinkercad_fit_guide.md` for the enclosure outline, and `Docs/BOM_Kit_Only.csv` for the exact parts list.

### XIAO pin mapping

| XIAO | GPIO | Net / function |
| --- | ---: | --- |
| D0 | 2 | NC (strap; do not load) |
| D1 | 3 | TFT DC |
| D2 | 4 | TFT CS |
| D3 | 5 | Key matrix column 0 |
| D4 | 6 | Key matrix column 1 |
| D5 | 7 | Key matrix column 2 |
| D6 | 21 | TFT SCK |
| D7 | 20 | TFT MOSI |
| D8 | 8 | Row 0 input with pull-up (strapping-sensitive) |
| D9 | 9 | Row 1 input with pull-up (BOOT strap; check at boot) |
| D10 | 10 | Buzzer GPIO **held disabled by default** |
| 3V3 | — | TFT VCC and RST |
| GND | — | TFT GND and active-low BL |
| VBUS/BAT | — | Neither wired by the PCB; no internal battery |

J1 net sequence: **GND, 3V3, SCK, MOSI, RST(3V3), DC, CS, BL(GND)**. Never presume the shipped display has that physical header order; map each jumper to its printed label before first power. Diode cathode stripe goes to **K1–K6 (switch side)**, anode to the appropriate **ROW**.

## Verification evidence — Rev D

| Validation | Observed result |
| --- | --- |
| Native KiCad schematic ERC | **0 errors / 0 warnings** |
| Native KiCad PCB DRC after native ground-zone refill | **0 violations** |
| Schematic-vs-PCB parity | **0 conflicts** |
| Native unrouted/unconnected pads | **0** |
| Native pad-geometry parity | **56/56 exact intended positions (±0.015 mm)** |
| Copper routing and GPIO fail-safe regression tests | **Pass** |
| Clock/alarm and timer/stopwatch C++ unit tests | **Pass** |
| Real Arduino ESP32-C3 / Adafruit compilation | **Pass (no physical flash)** |

Native KiCad and copper-zone proof: [GitHub Actions run 40272574464](https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40272574464). Genuine ESP32-C3/Adafruit compile: [run 40272572429](https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40272572429). The Rev D GitHub workflows rerun these checks. Generated source is committed to the repository, while **production Gerbers are not released**.

## Functions requiring no new parts

- One programmable alarm with individually selectable weekdays; large portrait time display with **AM/PM**, optional date, and red/cyan/gold themes.
- Six-button setup for local date/time or alarm settings, **five-minute snooze**, and GGK trivia with a deliberate dismissal shortcut.
- Wi-Fi **NTP synchronization**, plus a PIN-protected local phone settings page for clock sync, caption, colors, date visibility, and alarm settings. Only connect on a trusted private network; the site uses **HTTP**, not TLS.
- Extra **1–90 minute countdown timer** and **stopwatch** using the existing six keys. Hold **Clock Set** for countdown, **Down** for stopwatch. Countdown completion is visual until the piezo is verified. See `Firmware/README.md`.
- Firmware retains an audio-hold by default and will not assume any extra LEDs, speakers, RTC or backlight driver.

## Mechanical constraints

The board uses **15.9 mm switch pitch** to remain below Hack Club's ~100 mm guideline. **Standard full-size 1U/DSA keycaps cannot fit all six switches in that width**. Six custom **≤15.4 mm wide** printed keycaps are required, plus a physical 1:1 switch/housing fit test. If the real MX housings bind even without caps, the board must be reworked rather than forced.

The display is **off-board** and attached by eight wires; the faceplate needs final dimensions from the actual shipped part. Two M3 holes support the upper stem while the printed enclosure supports the lower PCB. Keep the USB-C cable from flexing XIAO joints.

## Power and safety limits — important

**Passing ERC/DRC does NOT prove the physical assembled device is safe if mis-soldered, safe in bed overnight, or usable without power.**

- **USB-C wall adapter:** use a reputable, correctly rated certified 5 V adapter and cable, **only after** inspecting every solder joint, polarity and output voltage, checking shorts with a multimeter, and supervised current/temperature testing.
- **Wall unplugged, USB connected to power bank:** possible with a reputable protected 5 V USB power bank that is tested to **remain on throughout the night**. Unplugging every power source shuts the clock off.
- **No internal battery:** BLARE's base kit includes no battery. Do not wire or solder a loose Li-ion cell to the XIAO to improvise standalone operation.
- **No guaranteed solder-fault protection:** there is no dedicated PCB fuse, reverse-polarity protection for a miswired TFT, battery charging/thermal protection circuit, or independent power cutoff. Such failures can damage electronics and potentially cause overheating.
- **Sound held disabled:** the 3.3 V buzzer's precise model, load and passive/active behavior are unknown; verify before enabling buzzer GPIO. Do not rely on this alarm to wake you until physical audio is validated.
- **Backlight permanently on:** the kit's active-low BL line is grounded; software cannot turn it off or guarantee energy savings. No RTC or protected timekeeping during power loss.

Before any overnight use, follow the complete **`Docs/SAFETY_FIRST_POWER.md`** checklist, have an adult with electronics experience inspect the assembly, run a supervised thermal trial, and use another dependable alarm. Physical product approval remains **false** in `Docs/RELEASE_GATES.json`.

## Files

- `PCB/jjkspeakerpcb.kicad_pcb`, `.kicad_sch`, `.kicad_pro`, local libraries — editable design and filled copper zones.
- `Firmware/GGK_Alarm/GGK_Alarm.ino`, `AlarmLogic.h`, `TimeTools.h`, `BoardConfig.h`, `secrets.example.h` — firmware; Wi-Fi credentials are not committed.
- `Docs/` — BOM, mechanical details, safety, power choices, engineering evidence.
- `Tests/` — KiCad physical-pad position, native GND refill, host logic, GPIO, and independent routing regression checks.
- `.github/workflows/` — repeatable KiCad ERC/DRC and real Arduino board compile.

**A manufacturing ZIP, confirmed assembly, and permission for unattended bedside operation have NOT been issued.**
