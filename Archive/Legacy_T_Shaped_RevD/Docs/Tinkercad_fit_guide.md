# GGK Alarm — Tinkercad mechanical fit guide (Rev D)

PCB maximum envelope: **99.3 mm wide × 99.3 mm tall × 1.6 mm thick**.
The outline is an inverted **T**: top display stem nominally x=31.0..69.0 mm,
y=0.35..75.2 mm. Key bar x=0.35..99.65 mm, y=75.2..99.65 mm.
The sharpest corner is chamfered; refer to `PCB_Outline_for_Tinkercad.svg`
for exact polygon. All coordinates below are measured from the upper-left
of that nominal 100×100 coordinate frame, with positive y downward.

Six switch/key stem center positions:

| Switch | X mm | Y mm | Function (ONLY firmware/enclosure) |
|---|---:|---:|---|
| SW1 | 10.25 | 89.50 | UP |
| SW2 | 26.15 | 89.50 | DOWN |
| SW3 | 42.05 | 89.50 | TIME SET |
| SW4 | 57.95 | 89.50 | CLOCK SET |
| SW5 | 73.85 | 89.50 | SNOOZE |
| SW6 | 89.75 | 89.50 | ALARM ON |

**15.9 mm spacing does NOT fit six standard 1U keycaps**, whose standard
switch spacing is 19.05 mm. Make six <=15.4 mm wide keycap bodies with
no spikes extending sideways into neighbors. Print and dry-fit a plate
with 15.9 mm spacing BEFORE approving electronics production.

Mechanical M3 hole centers: **H1 (35.6,38)** and **H2 (64.4,38)** ONLY. Holes H3 and H4 were removed from the final Rev D PCB because of interference with diode/switch routing. Hole diameter 3.2 mm. Design a captive ledge and standoffs in Tinkercad to support the **entire lower horizontal keyboard bar** without compressing switch solder joints. Metal fastener heads/heatset inserts must not touch copper.

USB-C belongs at the very top of the narrow stem around (50,0). The XIAO is mounted **on the back**; leave an accurately measured USB opening and enough space for cable bending without putting force on the PCB/module solder pads.

The drawn TFT module reference box is **21.08 × 73.15 mm** centered around x=50; this is NOT a confirmed measurement of the shipped BLARE kit module. The real kit display is attached via an 8-conductor jumper cable and does not sit directly on the PCB. Leave room for connector wiring, and measure the shipped module before finalizing its faceplate.

At least 0.3–0.5 mm allowance around printed mechanical fits is a starting point, not a guaranteed tolerance; adjust to your printer. Avoid heatset inserts touching copper. Make removable access for repairs, venting for ESP32/buzzer, and no exposed wiring near the bed.
