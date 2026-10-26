# GGK Alarm / BLARE — Electrical pin map and safety gate

## Six-switch, diode-isolated 2×3 key matrix

ESP32-C3 outputs: **D1/GPIO3 = ROW_LEFT**, **D2/GPIO4 = ROW_RIGHT**.
Inputs with internal pull-ups: **D3/GPIO5 = COL_TOP**, **D4/GPIO6 = COL_MIDDLE**, **D5/GPIO7 = COL_BOTTOM**.

| Switch | Function | Column net | Row net | Diode |
|---|---|---|---|---|
| SW1 | UP | COL_TOP | ROW_LEFT | D1 |
| SW2 | DOWN | COL_TOP | ROW_RIGHT | D2 |
| SW3 | OK | COL_MIDDLE | ROW_LEFT | D3 |
| SW4 | SNOOZE | COL_MIDDLE | ROW_RIGHT | D4 |
| SW5 | BACK | COL_BOTTOM | ROW_LEFT | D5 |
| SW6 | SKIP | COL_BOTTOM | ROW_RIGHT | D6 |

Electrical path on a pressed key: **column input (pulled up) → switch pin 1 → switch pin 2 → diode ANODE (pad 2) → diode CATHODE/striped end (pad 1) → selected LOW row output**. With other row driven HIGH, the diode prevents ghost currents. Before flashing firmware, verify exact switch/diode physical pin mapping with a multimeter.

## TFT header (J1), separate from board

| J1 pin | Screen label | Wire |
|---|---|---|
| 1 | GND | GND |
| 2 | VCC | XIAO 3V3 output, **NOT VBUS 5V** |
| 3 | SCL | XIAO D6 / GPIO21 (SPI SCK) |
| 4 | SDA | XIAO D7 / GPIO20 (SPI MOSI) |
| 5 | RST | 3V3 (no MCU GPIO) |
| 6 | DC | XIAO D8 / GPIO8 (boot strap pin: only screen CMOS input) |
| 7 | CS | XIAO D9 / GPIO9 (boot strap pin: only screen CMOS input) |
| 8 | BL | GND, active-low backlight ON |

Verify ESP32-C3 strapping on physical reset, especially screen CS on GPIO9. RST tied high is the BLARE example, but some ST7789 modules require a clean reset sequence. The TFT is 76×284 pixels; physical width/height/PCB must be measured in kit.

## Piezo and power

- XIAO D10/GPIO10 to BZ1 pin 1; BZ1 pin 2 to GND.
- Kit calls it a **3.3V Piezo Buzzer**, but manufacturer current draw, internal drive, and polarity are not provided in the user-supplied docs. This PCB MUST NOT be assembled/powered until a low-current GPIO-direct passive piezo is independently verified. A driver redesign may be required; software PWM does not fix current limits.
- XIAO D0/GPIO2 and XIAO VBUS are intentionally left NC; avoid GPIO2 strap loading.
- Board has no lithium-cell connector, battery charging circuitry, RTC or mains input. Power only by USB-C with suitable regulated 5V, e.g. an always-on USB power bank. Power bank may auto-shutoff at low draw: test this.
- Backlight BL hard grounded => no real sleep-current reduction or adjustable physical brightness. A screen-black software theme does NOT switch off LED backlight.
- Wi-Fi time sync; after full power loss clock time is unknown until reconnected. An RTC with coin cell would be separate additional hardware.

## Mechanical

Board custom polygon fits bounding rectangle **96 mm × 95 mm**; 2-layer 1.6mm nominal. 6 MX key switches are front through-hole, XIAO and buzzer are on the back, TFT via separate 8-pin header at the back. Mounting holes H1–H4 are 3.2mm NPTH for M3 screws. Avoid placing metal hardware directly against copper near holes. Tinkercad enclosure must provide USB, piezo vent, TFT slot, key travel and reasonable tolerances.

## Submission

Source PCB, schematic, project, ERC/DRC screenshots, STEP full enclosure (Tinkercad exports STL/OBJ, not necessarily STEP), Gerber ZIP and BOM should be reviewed before BLARE submission. This repo does not yet contain a fabrication approval.
