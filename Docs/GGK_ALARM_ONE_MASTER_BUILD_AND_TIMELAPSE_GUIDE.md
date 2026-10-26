# GGK Alarm — One Master Guide for BLARE (Rev D)
**Built around the original Hack Club BLARE kit, six MX switches, a portrait 2.25-inch ST7789 TFT, and one Seeed XIAO ESP32-C3.**

**Start here:** https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare

**SAFETY/STATUS: An electrically validated *design* is NOT proof that any soldered build is safe. Do not turn a self-soldered board on unattended or put it beside bedding until an electronics-experienced adult has visually inspected it, tested for shorts, tested voltage/current, and completed observed thermal operation. This design does not tolerate arbitrary soldering mistakes. The kit has NO battery. The buzzer is intentionally DISABLED in firmware by default.**

## Part 1 — What you are actually submitting and recording

BLARE has **two phases**:
1. **Design:** use Lapse to record your real work in KiCad, firmware, CAD and testing; submit a source repository with a working design to the eligible Stardance BLARE project. A design review and kit award come before physical assembly.
2. **Build:** when the approved kit and professionally fabricated PCB arrive, film and document the real soldering, assembly, tests and the device running; submit a real demonstration for the build phase.

BLARE's main site says the V2 program ended September 30, 2026, while Stardance still lists a BLARE mission. Only the project dashboard and Hack Club reviewers can confirm current eligibility. **Do not assume that merely creating a project guarantees a kit or grant.**

**Timelapse and evidence:**
- Open https://stardance.hackclub.com/missions/blare, your project, and https://lapse.hackclub.com. Select the Hackatime project that Stardance assigned to the hardware project.
- Record your actual work (screen recording for KiCad/Tinkercad/programming; camera/timelapse for soldering/assembly). Save recordings and write short, truthful devlogs after real progress.
- Film your own activity; do not claim assistant-generated files or time as hours you personally worked.
- Save screenshots of schematic, PCB with routing, 3D enclosure, Arduino compiling, and successful physical tests.
- Once physically finished, film a clear live demo of time, all six buttons, and whatever alarm features have been electrically verified. Do not simulate a working buzzer if the piezo is still unverified.
- Keep a smartphone backup alarm while prototyping.

## Part 2 — Exact project and parts

The current Rev D board is 99.3 x 99.3 mm, 1.6 mm FR4, narrow inverted-T shape. The TFT mounts to the **case in front** and is connected by eight jumper wires; the screen is NOT soldered directly over the PCB. The XIAO sits on the **PCB rear** near the top. The XIAO's own USB-C jack is the sole power/programming port, accessed through a top case opening.

Kit parts used:
- 1 Seeed XIAO ESP32-C3 board; 1 2.25-inch 76x284 ST7789 TFT.
- 6 of 12 available MX mechanical switches; 6 of 12 1N4148 through-hole diodes.
- 1 of the included 8-pin 2.54 mm male headers; 8 included female-to-female jumper wires.
- The supplied 3.3 V piezo **only after confirming its electrical type and load**; otherwise leave it unmounted and muted.
- Two M3 screw locations in the PCB's display stem, supported by available M3 screws/inserts. The case must also cradle the wide switch bar.
- Six narrower **custom 3D-printed MX-stem keycaps** in your chosen GGK red/black style. The kit's regular DSA caps do not fit at 15.9 mm spacing; no sideways spikes between neighboring keys.
- A reputable certified 5 V USB-C power adapter and cable **or** a protected external USB power bank with its own tested continuous-output behavior. These are power sources, not additional PCB electronics.
- NO soldered internal battery, no internal charging wires or bare Li-ion cell.

Tools, not electronic components: computer for KiCad/Arduino/Tinkercad, soldering iron and appropriate solder, magnifier, non-conductive mat, multimeter with continuity/diode/voltage ranges, safety glasses, ventilation, fine tweezers, flush cutters, correct screwdriver, and adult with practical electronics experience. If you cannot test for shorts/voltage, **stop before first power**.

## Part 3 — The six buttons and the matrix

Along the bottom, from LEFT to RIGHT:
1. SW1 UP — raise a setting / move selection up.
2. SW2 DOWN — lower a setting / move selection down.
3. SW3 TIME SET — edit clock/date; long press for info; exit timer/stopwatch.
4. SW4 CLOCK SET — edit alarm time/days; confirm a trivia answer; long press for countdown timer.
5. SW5 SNOOZE — during sounding alarm, snooze five minutes; **hold** to dismiss. In settings, back/cancel; in timers, reset.
6. SW6 ALARM ON — short press alarm enabled on/off; long press cycles red/cyan/gold themes; in weekday editor toggles selected weekday.

Electrically this is a **2-row x 3-column diode matrix**; it uses five MCU GPIOs for six keys. SIX diodes, not six GPIO-per-key wires. Do not bypass the diodes with jumper wires.

**Diode polarity:** each diode's stripe (cathode) must connect to the **individual switch's K1..K6 net (D1..D6 pad 1)**. The unstriped end (anode) connects to the corresponding ROW line (D1..D6 pad 2). Confirm the pad number against the actual KiCad diagram and with a meter; do not rely on facing direction in an image.

## Part 4 — XIAO and TFT wiring (verify by pin label)

This is the Rev D KiCad mapping: XIAO **D1 GPIO3 → TFT DC**; D2 GPIO4 → TFT CS; D3 GPIO5 → column 0; D4 GPIO6 → column 1; D5 GPIO7 → column 2; D6 GPIO21 → TFT SCL/SCK; D7 GPIO20 → TFT SDA/MOSI; D8 GPIO8 → row 0 INPUT_PULLUP; D9 GPIO9 → row 1 INPUT_PULLUP; D10 GPIO10 → potential piezo drive; D0 GPIO2 is deliberately unused. 3V3 supplies the TFT; GND is common. GPIO8/9 are boot-strapping sensitive: **do not force their logic level during startup**. The firmware is designed to keep rows input-only, but startup with pressed keys still needs actual hardware verification.

**PCB J1 header, pin-by-pin:**
| J1 pad | Electrical net | Match to the actual display's printed pin name |
|---|---|---|
| 1 | GND | GND |
| 2 | 3V3 | VCC (3.3V only) |
| 3 | DISP_SCK | SCL / SCK |
| 4 | DISP_MOSI | SDA / MOSI |
| 5 | 3V3 | RST / RES |
| 6 | DISP_DC | DC |
| 7 | DISP_CS | CS |
| 8 | GND | BL, only if the exact kit's backlight is active LOW |

**This table tells you the PCB pad order, NOT the screen module's physical left-to-right pin order.** Follow each module's printed label to the matching J1 pin individually with the included wires. Color and position alone are NOT sufficient. Never connect 5 V/VBUS directly to the TFT's VCC. The ground-connected active-low BL means the backlight remains on as long as powered: firmware can draw black, but cannot electrically switch off this display backlight.

The screen's reported resolution is 76 x 284 **portrait**. The firmware displays large hours/minutes in stacked lines with AM/PM; the kit screen is too narrow for full huge '10:24 AM' all on one line.

## Part 5 — Record the *design* and verify everything BEFORE ordering

1. Open the latest main-branch files after the Rev D safety PR has been merged. Clone or download ZIP on your computer; keep folders intact.
2. In KiCad open **PCB/jjkspeakerpcb.kicad_pro**, then the schematic and PCB. Do not start from the earlier Rev B/Rev C download files or from concept-art screenshots.
3. Verify exactly: six switches; six diodes; XIAO; 8-pin J1; buzzer footprint if validated; two mechanical holes. No labels under keys, no decorative artwork.
4. Confirm the electrical net map against Part 4, confirm both diode ends, and confirm the actual kit TFT pins. Verify native KiCad **Inspect → Electrical Rules Checker** reports **zero errors/violations**; in PCB Editor refill ground zones using **B**, then **Inspect → Design Rules Checker** and require zero copper/short/unconnected/clearance violations and zero schematic parity issues. Do not dismiss shorts or use rule exclusions to silence them.
5. Verify real USB-C clearance and XIAO board orientation. Check the KiCad footprint is the intended physical mounting method; it's an SMD/castellated mount, not an arbitrary Uno-style socket.
6. BEFORE you approve PCB manufacturing, obtain measurements or a reliable dimensioned drawing of the exact shipped TFT, buzzer, physical MX switch housings and six narrow cap bases. The older visual TFT reference box is **not** an audited module size.
7. Record genuine personal CAD/engineering work with Lapse. The GitHub repo should carry your final sources and evidence. Ask Hack Club to confirm your project/kit/grant eligibility before spending money.
8. Once the physical fit and final native ERC/DRC pass, in KiCad use fabrication outputs to create **Gerbers + drill** files, ZIP them, view them in a Gerber viewer, recheck 2-layer outline size <100 mm both ways, and use the BLARE/JLCPCB grant if actually awarded. **No manufacturing ZIP was approved or released automatically by this guide.**

## Part 6 — Tinkercad case, mounting, and GGK visuals

**Use actual physical dimensions before your final print.** The PCB's nominal overall envelope is 99.3 x 99.3 mm; its stem is about x31..69 mm, y0.35..75.2 mm; six switch centers (x,y, millimeters from top-left of nominal 100x100 frame):
- SW1 (10.25, 89.50)
- SW2 (26.15, 89.50)
- SW3 (42.05, 89.50)
- SW4 (57.95, 89.50)
- SW5 (73.85, 89.50)
- SW6 (89.75, 89.50)

Spacing is **15.9 mm**; standard MX spacing is around **19.05 mm**. The special caps must be no more than **15.4 mm wide** at their closest point; verify the *actual MX housings* have enough room too. Print a small straight six-key spacing gauge/test plate first, insert the switch bodies and keycaps, and press all six to prove no binding. If switch housings rub, adjust the PCB design, NOT the plastic by force.

Only two M3 PCB holes: H1 (35.6,38), H2 (64.4,38), **3.2 mm drilled**. Do not drill extra holes in the copper board. The lower key bar needs its own supportive PLA cradle/ledge. Design at least ~0.3–0.5 mm trial-fit allowance around PCB walls and connectors, then adjust with a test print.

Tinkercad workflow:
1. Switch units to **millimeters**. Use the included **Docs/PCB_Outline_for_Tinkercad.svg** for top-down geometry reference; white SVG circles are **only location markings** and may not become real holes on import. Cut M3 holes manually in your enclosure geometry.
2. Create a back shell matching the T-shaped PCB plus a small safe perimeter clearance. Add stand-offs at the two holes and a broad **nonconductive support ledge under the key row** without touching diode leads, copper or SMD pads.
3. Leave a slot at the top for the XIAO's actual USB-C connector and enough cable-bend clearance. Do not put mechanical strain on soldered module contacts.
4. Build a removable front face with a **portrait TFT window measured from the delivered part**, not invented from the drawn outline; run eight screen wires away from the switch stems and screw bosses.
5. Make six red/black GGK-styled narrow keycaps, with crown/spike decoration upwards rather than sideways into neighboring switches. Do not put conductive metal decoration near PCB power.
6. Add buzzer grille only after verifying buzzer; keep airflow around the XIAO; make the case inaccessible to fingertips at solder pads, dry, with no pinch point for cables.
7. Print a rough fit prototype in PLA; test, correct, then produce final shell and separate STEP/STL files. Include an assembled STEP for BLARE submission where required; STL-only exports are not equivalent to an editable CAD source.

## Part 7 — Program the XIAO before soldering it (easier)

1. On a computer install **Arduino IDE 2.x**. Under Preferences, add the ESP32 board package index URL:
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
2. In Board Manager install '**esp32 by Espressif Systems**'; in Library Manager install '**Adafruit GFX Library**' and '**Adafruit ST7735 and ST7789 Library**' and any prompted dependencies.
3. Open **Firmware/GGK_Alarm/GGK_Alarm.ino**, keeping the adjacent source headers in the SAME folder: AlarmLogic.h, TimeTools.h, BoardConfig.h, and a local secrets.h.
4. Copy **secrets.example.h** to **secrets.h**. Enter Wi-Fi SSID/password for your own trusted home Wi-Fi, your actual timezone, and a unique portal PIN at least six characters. NEVER add secrets.h to public GitHub, a recording, or a photo.
5. Keep **GGK_BUZZER_VERIFIED = 0** and **GGK_HARDWARE_INSPECTED = 0**. Don't change these just to get sound before hardware review. These flags are acknowledgements, not fault-proof sensors.
6. Select board **Seeed XIAO ESP32C3** and its USB port in Arduino IDE. Use **Verify/Compile**, then Upload using XIAO's USB-C while the unmounted MCU sits safely on a nonconductive surface. Check the IDE shows upload success; if not, follow Seeed's board-specific boot/recovery instructions rather than shorting random pads.
7. Unplug USB before assembling/soldering. The screen and keys won't operate until they are physically connected.

## Part 8 — Assemble the PCB in real life (adult-supervised)

Only begin when the manufactured PCB and exact kit parts are in hand, the BOM agrees with the files, the physical part sizes and diode direction are confirmed, and the board has no visible fabrication defects.

1. Record your **real** build on a stable, ventilated, nonflammable workbench; safety glasses; clear space; USB unplugged; battery absent. Photograph all parts before assembly.
2. Inspect bare board both sides under light. Check XIAO castellated pad row order, J1 footprint, MX locations, every via, and mounting holes. Compare to KiCad printout/placement file. If anything doesn't match, do not populate.
3. Fit **D1..D6 1N4148 diodes** on the specified back-side holes. Each stripe points toward **its own K switch net/pad 1**; anode to row/pad 2. Confirm all six in **diode mode** before soldering. Solder one at a time with appropriate heat and ventilation. Do not overheat or stress the glass bodies. Trim only with eye protection.
4. Dry-fit all **six MX switches** in their exact holes first. Do NOT solder until all switch housings and your narrow keycaps can coexist without touching. Test-fit the 3D case front. Then solder, maintaining straight alignment.
5. Fit and solder the **eight-pin male TFT header J1 on the correct face of the board**. Verify pin 1 as in the KiCad silkscreen/schematic. The screen remains off-PCB on eight F–F leads.
6. **XIAO back SMD/castellated mounting:** this is the most delicate operation; have an electronics-experienced adult perform or supervise. Hold exact orientation so USB-C exits through the intended case-top opening. Secure first corner joint, check all pins, then carefully solder remaining lands without bridges. Do not apply pressure to USB connector while molten.
7. Do **not** solder/populate the piezo until you know the actual part type, current and polarity; the firmware intentionally has audio disabled. If it is not a verified low-current passive piezo safe for direct GPIO, the present circuit **cannot safely drive it** without a redesign.
8. Clean flux if needed as appropriate to materials, inspect solder under magnification, confirm no whiskers/splashes, and do not attach the TFT wires until the cold continuity checks pass.

**Stop immediately if you accidentally bridge pads, lift copper, crack a module, reverse a component, or damage USB. Do not 'try powering it anyway.'**

## Part 9 — First-power electrical checks (mandatory, adult)

With USB and any battery **disconnected**:
1. In ohms/continuity mode, check 3V3 ↔ GND for an unintended hard short; check adjacent XIAO pads, opposite diode pads, and the J1 supply pins. Capacitor charge/discharge can briefly trigger meters; resolve any suspicious result rather than assuming safety.
2. Check there is NO electrical connection putting USB 5 V onto TFT VCC, logic signals or 3V3. Confirm each 1N4148 diode conducts in only the specified direction in diode mode.
3. Check buttons unpressed are not shorted and each button works; make sure GPIO9 is not grounded by a miswire at boot. The current design has no guarantee against every solder fault.
4. Leave **TFT disconnected, piezo unpopulated**. On a current-limited USB test supply (with an adult), power the XIAO briefly. Verify firmware starts and the board has no obvious abnormal current/voltage/temp. If it cycles, smells, warms rapidly, or glitches: unplug.
5. Measure 3V3 ↔ GND with the meter; expect about **3.3 V**. If the rail exceeds **3.6 V**, stop immediately and investigate. Never touch exposed powered solder joints.
6. Power OFF. Wire the TFT by **matching each individual J1 pin function to the physical screen's printed pin**, not by lining up two 8-pin headers blindly. Connect every wire with all power off, check again, then briefly power and check vertical graphics.
7. Test each key individually and in combination. Test with some keys held during restart only after a verified boot, checking for a strapped-boot failure. Inspect voltage and thermal behavior again.

Do not use bedding, mattress, rug or paper as a test surface; no charging cell anywhere on the board. Do not run the clock in bed while testing.

## Part 10 — Test every feature

Use the six keys left-to-right as in Part 3. Startup alarm is intentionally disabled. Perform supervised checks:
1. Clock shows hour, minute, and **AM/PM** in the correct timezone. Time Set cycles hour → minute → month → date → year → saves on final press. UP/DOWN adjust. With Wi-Fi off, date/time settings should function as long as powered.
2. Clock Set cycles alarm hour → minute → weekday selection. UP/DOWN change values; Alarm On toggles the selected weekday; Clock Set saves. Confirm weekday selection by reading the screen.
3. ALARM ON briefly toggles alarm state; hold it to cycle screen theme. The alarm should not accidentally be active while first calibrating.
4. During an alert, UP/DOWN select a GGK trivia answer; CLOCK SET confirms a correct answer; **short SNOOZE** delays five minutes; **hold SNOOZE** dismisses. Buzzer stays silent until physically verified.
5. Hold CLOCK SET on home for countdown timer (1–90 minutes): UP/DOWN set length; CLOCK SET start/pause; SNOOZE reset; TIME SET exit.
6. Hold DOWN on home for stopwatch: CLOCK SET start/pause; SNOOZE reset; TIME SET exit.
7. Check Wi-Fi NTP sync or phone sync when connected to your private Wi-Fi. From the phone on that network open **http://ggk-alarm.local/** (or ESP32's local IP), enter PIN, change the **caption, alarm days/time, alarm on/off, date visibility and red/cyan/gold theme**. The portal is **local HTTP, not HTTPS**—never forward port 80 or expose it publicly.
8. Verify loss/restoration of USB: the settings should persist but time may need re-sync. With **all** USB power unplugged the clock and alarm stop; no internal RTC/battery.
9. Test a full 24-hour cycle including day change and backup phone alarm. The software auto-stops alarm after at most 180 seconds—this is for reducing prolonged sound, not guaranteed waking.

## Part 11 — Sound and overnight power are NOT yet approved

The kit lists an unspecified **3.3 V piezo buzzer**, but no validated model/current in the project. Do not connect random active electromagnetic buzzers directly to ESP32 pins. The firmware starts with sound disabled. **Do not turn on sound solely by editing both flags to 1**. Confirm part identity, current draw, polarity and allowable driver method with a supervising adult first, and document bench testing. The standard piezo cannot play a full MP3 recording of an anime opening; after verification, it can at most play suitable simple tone sequences. Use an original GGK-inspired melody rather than relying on a copyrighted opening.

**Wall power:** use a reputable 5 V USB adapter/cable after first-power tests. **Away from wall:** use an external protected USB-C power bank, and first prove that the bank doesn't automatically turn off under the clock's load; test actual runtime. **Every power source unplugged:** device OFF; it will not keep time or ring. No internal Li-ion battery, protection PCB, charging battery cable, RTC, fuse or independent shutdown in the included kit. Don't invent a lithium pack workaround.

**Before any unattended use:** inspect/correct all joints, test with a current-limited supply, observe a multi-hour thermal run on a nonflammable surface, add proper ventilation and USB strain relief, use the exact production power source and full assembled case, repeat a supervised overnight-equivalent trial, and have an adult verify. This is still not a guarantee of zero faults. Use your phone as a backup alarm.

## Part 12 — Finish GitHub, video and Stardance submission

The public repo should eventually contain:
- **PCB/**: editable .kicad_pro, .kicad_sch, .kicad_pcb and custom footprint/symbol libraries.
- **CAD/**: assembled clock **STEP** with actual TFT, board, and all case parts (plus STL individual printable pieces).
- **Firmware/**: .ino and headers; **never** secrets.h.
- **Production/**: manufacturing Gerbers ZIP + drill files **only when verified for the approved PCB revision**; never guess or reuse an earlier version.
- **README.md**: what GGK alarm is, photos/screenshots of overall alarm, schematic, PCB, Tinkercad/assembled case, BOM, build details, test results, and demo link.

BLARE's published submitting guide asks for photos/screenshots of schematic, PCB, completed clock and case, a parts BOM, native design sources, production files, and firmware. Stardance additionally asks for legitimate Lapse/Hackatime work evidence and a live working physical demo after assembly. Upload an honest short video showing all buttons and display; make any silent-audio limitation clear. Link the exact GitHub commit used and the actual physical photos—not concept art.

**Important:** Do not claim the display, buzzer, power, temperature or USB have been physically tested when they have only passed software/EDA checks. No part of this text means the project is approved for manufacturing or overnight use. Only the inspected and physically tested board can move through those final safety gates.
