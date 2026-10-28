# GGK Alarm — first-power and overnight readiness checklist

**WARNING:** These checks reduce risk but cannot make a homemade PCB foolproof.
If you are not comfortable measuring electronics, have an adult with PCB/soldering
experience inspect it. Never power a visibly damaged/bridged board, never leave
an untested board powered unattended, and do not treat a USB phone charger as a
universal protection device. Do NOT add any battery while soldering/testing.

## Before ordering PCB

- [ ] Inspect schematic for exact U1 pin assignments and all 8 TFT wires.
- [ ] Run KiCad native `ERC` and `DRC` with zones filled: ZERO errors, no ignored shorts or unconnected pins.
- [ ] Compare U1 SMD footprint and all 22 lands to *official current* Seeed footprint. Ensure XIAO USB-C faces case opening.
- [ ] Obtain exact kit TFT/module dimensions, current, header orientation and reset/backlight pin descriptions. Check 3V3 not 5V.
- [ ] Verify piezo part marking/model; **if it takes more GPIO current than the XIAO supports, redesign with a driver** rather than guessing.
- [ ] Test-print key strip at 15.9 mm: 6 MX housings and custom narrow caps must click freely, no binding with neighbor, no stress on FR4.
- [ ] Confirm actual PCB outline <100 mm each dimension and all M3 screw heads clear copper and components.
- [ ] Print a box from Tinkercad with a lid, USB-C clearance, ventilation, buzzer grille and no exposed solder pads, metal hardware or wires.

## Before any power (adult supervised)

1. Remove the USB cable and any other power source. Work on a dry, non-conductive surface away from bedding or paper clutter.
2. Under bright light/magnification, inspect **every** XIAO castellated solder joint, diode orientation, header pins, switch solder joints, and accessible back/underside pads. Fix bridges, loose strands, cracked joints or sharp wire ends.
3. With a multimeter in continuity mode, check **3V3–GND is NOT a dead short**, and confirm each TFT signal is not accidentally shorted to adjacent header pins or VBUS. Resistances may vary with on-board capacitors; investigate readings instead of assuming all beep tests mean a short.
4. Confirm USB-C VBUS does **not** appear on the 3V3 or display control nets. Verify TFT wiring against actual screen labels; this is vital because 5V on a 3.3V pin can destroy hardware.
5. Verify each of the six 1N4148 diode bars points to the schematic cathode/net K1..K6 as marked in the footprint. Use diode-mode multimeter one diode at a time.
6. Check there is no battery and no charger lead, especially no bare lithium cell leads.
7. First turn on **only** the XIAO with the TFT connector unplugged and buzzer unpopulated. Use a current-limited USB test adapter / bench USB fixture if available; have a supervising adult read current and voltage. If power source current-limits, power cycles, becomes hot or voltage sags, unplug immediately.
8. Check the regulator output with a multimeter: 3V3 should be approximately 3.3V, not USB 5V. If a measured supply exceeds 3.6V at the 3.3V rail, disconnect immediately. Verify boot/reset and USB firmware upload before connecting peripherals.
9. Unplug power. Connect the TFT exactly one pin-to-pin, checking GND/VCC/RST/BL, then power and verify rendering. Disconnect and repair if anything warms unusually, flickers continuously, or smells.
10. Leave the buzzer **disabled in firmware** and unpopulated until the actual kit part/current is measured. Never bypass the build's AUDIO HOLD with a random 3.3V active buzzer.
11. Test six individual switches and combinations (including while booting and during flashing); no stuck button, unexpected reboot or overheated component is acceptable.

## Supervised reliability trial before bedside use

1. Start with an open enclosure on a fire-resistant work surface, observed by an adult. Test over a few hours with Wi-Fi on and screen active. Measure/monitor thermal behavior without touching exposed conductive points.
2. Interrupt power intentionally while an alarm is scheduled, then restore. Confirm the device reports lost time or resynchronizes via Wi-Fi; **never assume it retained the alarm moment while without power**.
3. Once the actual piezo is verified and a current-safe drive path exists, activate brief test patterns with close supervision. Press SNOOZE to mute immediately and hold SNOOZE to dismiss; verify maximum 180-second automatic timeout.
4. Test date changes, correct day selection, AM/PM noon/midnight, daylight-saving transition and no duplicate alarm after reset. Confirm alarm settings remain after unplug/replug.
5. Assemble in a smooth printed enclosure with strain relief and ventilation. The USB-C port must be accessible without stressing the XIAO solder joints; no direct contact with bedding, pillow, carpet or papers.
6. Run a **supervised or adult-monitored full overnight-equivalent trial**, including the exact adapter or power bank. If using a bank, observe no auto-shutdown or brownout after hours of low load. This is not proof of absolute safety.
7. Only after electrical and thermal signoff consider it as an *additional* bedside alarm; keep your phone/another dependable alarm as primary initially.

## Unplugged from wall vs unplugged from every power source

- **Wall unplugged but USB-C attached to a suitable protected USB power bank:** supported in principle, subject to power-bank auto-shutoff and runtime tests.
- **USB-C unplugged and no added internal battery:** board is OFF. No clock or alarm.
- **Internal battery added without BOM/connector/charge/protection validation:** NOT approved. The XIAO C3 has a lithium charger, but the BLARE kit omits protected batteries, battery power connectors, fuses, pack temperature sensing and suitable enclosure space. Charger presence is not a universal protection system.

## What a soldering error can do

- Solder bridges can short 3V3-GND or damage USB regulator and copper.
- Reversed/solder-shorted TFT VCC/GND or TFT VCC 5V can permanently destroy display/MCU.
- Pressed keys on a miswired row can ground a BOOT strap and prevent startup.
- A lithium battery with miswired or damaged contacts can overheat, swell or ignite.

There is **no way** to guarantee a home-soldered board is safe regardless of faults. The only responsible release process is checking and measuring the actual assembled item.
