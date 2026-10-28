# GGK Alarm Rev D — hardware design audit (October 25, 2026)

## Verified electrical design (NOT physical product approval)

The following were run in native KiCad 9 GitHub Actions against the generated Rev D source after regenerating the board and refilling both copper ground zones:

- 56/56 native XIAO/TFT/diode/switch pad coordinates matched the router manifest within 0.015 mm.
- Native KiCad ERC: 0 errors, 0 warnings.
- Native KiCad DRC after both GND zones filled: 0 violations.
- Native unconnected pads: 0; missing schematic/PCB connections: 0.
- Independent routing, 0.2 mm clearance, source/firmware safety tests: passed.
- Real Espressif Arduino XIAO ESP32-C3 compile using Adafruit GFX/ST7789 libraries: passed.
- Countdown/stopwatch tests include millis wraparound and pause/resume.

[Native KiCad run](https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40272574464)

[Real Arduino compilation](https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40272572429)

**Explicit hold:** manufacturing files / electrical activation / leaving it running beside bedding are not approved. The shipped TFT connector pin order, dimensions, buzzer current/type, 15.9 mm switch/keycap fit, XIAO physical solder joints, USB supply behavior, enclosure heat, and any overnight trial remain unverified.

The base kit has no battery. A 5 V wall adapter or external protected power bank via the XIAO USB-C provides power; fully disconnected operation is not implemented. No dedicated external fuse or blanket solder-error protection. The unverified buzzer is firmware-disabled by default.

## Corrective design changes from Rev C

1. Removed incorrect backside footprint/pad coordinate assumptions, including all 22 XIAO contacts.
2. Corrected both back-mounted TFT and piezo positions, and all six 1N4148 physical cathode/anode positions.
3. Removed H3/H4 holes near the lower keyboard bar because they intersected signal routing; enclosure supports bar.
4. Rebuilt copper traces and vias using the exact native KiCad pad coordinates.
5. Fixed copper zone syntax and filled both GND zones with native KiCad. J1 ground pad uses a locally solid zone connect, avoiding a starved thermal-spoke DRC violation.
6. Aligned project-local XIAO footprint with the exact backside board instance; ERC/DRC pass without suppressing errors.
7. Added firmware timer/stopwatch without additional parts. Real Arduino CI compiles the program.

The UI source-derived images are visualizations only; manufacturing acceptance comes from native KiCad ERC/DRC and physically inspecting real kit parts, not screenshots or custom geometry checkers.
