# GGK ALARM — BLARE Rev C engineering package

**STATUS: DESIGN + SOFTWARE PROTOTYPE. NOT APPROVED TO FABRICATE, POWER UNATTENDED OR RELY ON FOR WAKING.**

This revision rebuilds the user's uploaded blank `jjkspeakerpcb` KiCad project as a narrow vertical GGK alarm PCB: kit 76 × 284 portrait ST7789 TFT (connected by 8 F-F jumper wires), a single six-switch horizontal row, ESP32-C3 XIAO on the back with USB-C at the top, 3.3 V piezo footprint, six 1N4148 switch matrix diodes, and M3 screws. No side decoration or key silkscreen labels. The board is 99.3 × 99.3 mm, with 15.9 mm switch pitch.

## What was engineered in Rev C

- Corrected 2×3 keyboard diode orientation for LOW-driven columns and pulled-up row inputs.
- Reassigned XIAO D9/GPIO9 (BOOT strap) to a **pulled-up keyboard row input** rather than TFT CS. TFT DC and CS now use non-strapping D1/D2 GPIO; GPIO8 likewise a row input.
- Explicitly routed GND between U1, J1, and BZ1, so copper planes do not have to be filled to achieve basic GND connectivity.
- Existing copper and pad geometries independently checked for same-net connectivity and ≥0.2 mm spacing with a Python math checker; the checks found 0 unrouted pad networks and 0 violations below 0.20 mm in their geometric model.
- Added firmware that implements all six actual keys (no longer an incompatible four-key prototype), 12-hour portrait display with AM/PM, alarm/day editing, manual time/date editing, NTP Wi-Fi sync, 5-minute snooze, optional GK trivia dismissal, protected-local-PIN phone controls, and selectable display colors/title.
- Added host C++ behavioral tests, syntax-only firmware API stubs, manufacturing holds, electrical first-power checklist, full GPIO schematic map and Tinkercad enclosure dimensions.

## Exact pin mapping (KiCad U1)

| XIAO pin | GPIO | Board net/function |
|---|---:|---|
| D0 | 2 | NC. ESP-C3 strapping pin, intentionally unused |
| D1 | 3 | TFT DC |
| D2 | 4 | TFT CS |
| D3 | 5 | Matrix column 0 (SW1/SW2) |
| D4 | 6 | Matrix column 1 (SW3/SW4) |
| D5 | 7 | Matrix column 2 (SW5/SW6) |
| D6 | 21 | TFT SCK, output; UART boot activity may flash display |
| D7 | 20 | TFT MOSI |
| D8 | 8 | Matrix row 0 input with pull-up |
| D9 | 9 | Matrix row 1 input with pull-up (BOOT strap) |
| D10 | 10 | Buzzer drive GPIO, blocked until kit piezo electrically approved |
| 3V3 | – | 3.3 V output for TFT VCC and RST |
| GND | – | Ground and TFT active-low BL |
| VBUS | – | NC; USB-C is built into the XIAO |
| BAT underside | – | NC; **no internal battery circuit** |

The TFT's *pin order* is J1: GND / 3V3 / SCK / MOSI / RST(3V3) / DC / CS / BL(GND). Verify the actual shipped BLARE screen and its labels; if they differ, STOP before connecting.

## BOM and scope

`Docs/BOM_Kit_Only.csv` lists everything sourced from BLARE and custom 3D-printed keycaps. **No additional USB-C connector, battery charger, 18650 cell, LiPo connector, speaker amplifier, or TFT was quietly added.** The display module must be the actual BLARE screen, not the generic 1.9-inch display in the previous fictional image.

### Important six-switch mechanical exception

BLARE supplies twelve full-size MX keycaps, but six 1U keycaps at standard 19.05 mm pitch need ~114.3 mm width, violating the recommended <100 mm PCB envelope. This board uses 15.9 mm pitch and therefore **cannot use six included full-size keycaps together**. Six custom narrow ≤15.4 mm-wide keycaps (and confirmation that the switches themselves fit) are mandatory. Check with an actual 1:1 switch-spacing test print before order. If they do not fit, choose a longer board or fewer buttons instead of forcing them.

## Power and overnight operation — STOP AND READ

**There is no safe claim of mis-solder-proof or guaranteed all-night operation.**

- Wired mode: a high-quality, standards-compliant USB-C cable and certified 5 V USB adapter power the XIAO. The USB-C connector is already on the XIAO. A correctly assembled device may be suitable for overnight operation **only after** electrical inspection, supervised burn-in, enclosure/heat checks, and a verified alarm cycle.
- Away from a wall outlet: plug the same USB-C into a reputable **external USB power bank** that stays awake under the load. You must run a full overnight no-dropout trial with that exact bank. It is still plugged into the USB power bank; it is **not an internal self-contained battery**.
- Fully unplugged: the BLARE kit contains no battery. The Rev C board cannot operate when **all** USB sources are disconnected. Seeed's XIAO has battery charging circuitry, but without a qualified protected battery, validated connector polarity, pack protection, current limits and mechanical isolation, an internal Li-ion path would introduce unacceptable risk.
- Do not solder an unprotected loose Li-ion pouch cell to the BAT pads. Do not test charging a battery in a closed or flammable enclosure. No lithium battery interface has been added to this revision.
- GPIO alone may NOT safely operate an unknown active or electromagnetic buzzer. The supplied "3.3 V piezo" part lacks an exact part number/current spec in the kit list. Firmware defaults to **AUDIO HOLD**. The output must remain disabled unless the shipped part is proven passive and low-current; otherwise add a properly sized transistor driver and associated parts in a later design.
- This kit PCB has **no dedicated external overcurrent fuse**; it cannot prevent all solder shorts, wiring reversals, overheating, or electrically unsafe adapters. A phone or powerbank's short-circuit protection is not a substitute for inspecting every connection.
- The TFT active-low BL pin is grounded, so its backlight remains powered. Black pixels or ESP deep sleep do **not** make a low-power battery alarm; proper backlight switching is an unbuilt future revision.
- No RTC battery, DS3231, GPS, or protected time backup is included. If input power disappears, device stops. It attempts NTP synchronization once connectivity returns, but the alarm **must not** be the only source you rely on to wake up.

### Electronics release blockers

1. KiCad `kicad-cli` is not available in this container (Debian package repository unreachable); **native KiCad schematic ERC and PCB DRC, refill, exact pad checks and exported production Gerbers have NOT been run**. Geometric route checks DO NOT substitute for them.
2. Actual kit 2.25-in TFT module pin order and outside dimensions remain unverified. Reference box on `Dwgs.User` is example-only.
3. Actual kit buzzer's part number, 3.3V current and passive/active behavior remain unverified. Verify before driving GPIO10.
4. Standard DSA keycap collision (15.9 mm vs 19.05 mm pitch) requires a physical printed fit check.
5. All 22 XIAO lands and USB-C external access must be confirmed against actual delivered board and case.
6. Verify diode band orientation (cathode pad1 to switch node; anode pad2 to row) matches both silkscreen/back-side view and KiCad generated netlist.
7. Run electrical continuity and polarity testing **before USB power**, then supervised current-limited bring-up. See `Docs/SAFETY_FIRST_POWER.md`.
8. Arduino `.ino` was host syntax-parsed against API *stubs*, and behavioral logic was unit-tested; it has not been compiled with genuine ESP32/Adafruit libraries or flashed to hardware. Real firmware compile and panel test mandatory.
9. Screen module/mechanical fit and enclosure ventilation must be measured and validated before enclosed continuous use.

## Project structure

- `PCB/`: editable KiCad `.kicad_pro`, `.kicad_sch`, `.kicad_pcb` and local symbol/footprint library; **no released Gerbers**.
- `Firmware/GGK_Alarm/`: Arduino `.ino`, alarm logic, GPIO map and Wi-Fi PIN template.
- `Docs/`: BOM, hardware constraints, safety test plan, geometry/connectivity reports, Tinkercad geometry.
- `Preview/GGK_Alarm_RevC_KiCad_PCB_Layout.png`: actual source-coordinate geometry plot; it is not a KiCad 3D viewer output.
- `Tests/`: C++ alarm logic tests, firmware API stub parse, copper connectivity checker.

## Validate software locally

```bash
python3 verify_board_geometry.py
python3 Tests/independent_connectivity.py
g++ -std=c++17 -Wall -Wextra -Werror -pedantic Tests/alarm_logic_tests.cpp -o /tmp/ggk_logic && /tmp/ggk_logic
g++ -std=c++17 -Wall -Wextra -Werror -pedantic -ITests/fake_arduino -x c++ -fsyntax-only Firmware/GGK_Alarm/GGK_Alarm.ino
```

**Status is DESIGN HOLD until the KiCad, fabrication, electrical, thermal, and all-night tests pass.** No Gerber ZIP for ordering is included intentionally.