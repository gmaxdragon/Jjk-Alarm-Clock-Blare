# GGK Alarm / JJK BLARE — KiCad engineering draft v0.1

A compact Sukuna / Malevolent Shrine-inspired alarm clock for **Hack Club BLARE**. The front uses six MX keyboard switches arranged symmetrically around the planned portrait TFT. The red-and-black crown/spike aesthetic belongs primarily to the 3D-printed Tinkercad enclosure and keycaps.

**BUILD STATUS: PCB SOURCES ARE ENGINEERING DRAFTS, NOT FABRICATION-APPROVED.** Read `Docs/PINMAP_AND_SAFETY.md` and check the native KiCad ERC/DRC workflow and hardware kit before ordering.

## Project source

- `PCB/jjkspeakerpcb.kicad_sch`: native KiCad schematic, pins and matrix-diode nets.
- `PCB/jjkspeakerpcb.kicad_pcb`: editable 96 × 95 mm two-layer custom-shaped PCB; attempted routed traces and ground zones. KiCad itself must validate clearance and connectivity.
- `PCB/jjkspeakerpcb.kicad_pro`: project settings.
- `scripts/fill_zones.py`: KiCad pcbnew Python zone fill, not a motor/electronics control.
- `.github/workflows/kicad-validate.yml`: software-only ERC, DRC, SVG/gerber preview audit. No board ordered.
- `Docs/PINMAP_AND_SAFETY.md`: kit BOM, pinout, diode orientation, and design holds.

## What the kit provides

1 Seeed XIAO ESP32-C3; 6 of the 12 included MX switches; 6 of the 12 included 1N4148 diodes; a 2.25-inch ST7789 76×284 TFT connected with the kit's eight-pin header/jumper wires; 3.3V piezo; four M3 mounting holes. No external PCB components are budgeted.

## Software feature plan

One alarm with selectable weekdays, Wi-Fi/NTP synchronization, five-minute snooze, short key trivia, easy SKIP, optional red/black animations and original buzzer melodies. Deep-sleep scheduled wake, reliable off-grid timekeeping, battery charger and amplified copyrighted music **are not part of this v0.1 PCB**.

## Hardware/assembly holds

- The kit's **exact buzzer electrical specification** must be verified before powering from ESP32 GPIO. If it is a high-current active/magnetic buzzer, a transistor driver and resistor are required and this direct-piezo connection must be revised.
- TFT RST is wired to 3V3 and active-low BL to GND per BLARE documentation; **backlight stays on** unless hardware revised.
- Use XIAO **USB-C input from a 5V USB supply or power bank with always-on mode**. Do not connect a bare LiPo to USB 5V or 3V3.
- Time is not protected against full power loss without added RTC/battery backup. Wi-Fi sync is a functional dependency for correct startup clock time.
- PCB is a substrate for key switches: screen mounts separately within the Tinkercad case. Do not assume any TFT module dimensions without measuring the shipped screen.
- Keycap spikes must be rounded and kept clear of fingers, moving keys, and nearby screen.
- BLARE review still needs a full case/STEP and demo evidence.

## KiCad DRC and original files

The original attached `jjkspeakerpcb.kicad_*` project was **blank**. These files are newly constructed, not edits of a routed original. Actual fabrication requires zero KiCad ERC/DRC errors and inspection of F/B copper, plated switch holes, mounting clearances, connector orientation, and 3D fit.
