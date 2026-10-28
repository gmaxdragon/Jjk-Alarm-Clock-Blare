# JJK Alarm compact submission inventory

## Current revision

The submission-facing design is the **95 × 95 mm** compact PCB and matching revised mechanical assembly. The original **125 × 110 mm** version remains in `Archive/Original_125x110`. Original uploaded screenshots and source geometry are preserved. Nothing was uniformly scaled to fake compliance with the supplied under-100-mm PCB guidance.

## Required files prepared

| Owner-supplied BLARE requirement | Current evidence |
| --- | --- |
| Complete clock STEP in CAD | `CAD/JJK_Alarm_Assembly.step`, 50 reimported valid solids |
| KiCad project, schematic and PCB | Matching files in `PCB/` |
| Firmware source | `Firmware/JJK_Alarm/` |
| Production Gerber ZIP | `Production/gerbers.zip`, seven layers plus PTH and NPTH drill files |
| Separate case-part exports | Three checked STL production parts; analytic panel/retainer STEP files also supplied |
| Overall clock image | Actual revised assembly render in README |
| Schematic image | Owner's supplied screenshot; electrical connections unchanged |
| Current PCB image | Native KiCad plot of compact board |
| Case/assembly image | Revised exploded CAD view and electronics view |
| BOM | README includes current electronic parts, normal kit keycaps, case parts and fasteners |
| DRC zero errors | `Production/Checks/DRC.rpt`, zero violations and unconnected pads |
| Fit allowances | Documented design clearances and reference-model collision checks in CAD reports |
| Committed files | Current repository commit and source/asset manifests |

## Checks performed

- Original-versus-compact component/pad net assignments retained; no pin pitch or hole scaling.
- Native KiCad ERC, DRC, schematic parity and zone refill.
- Real XIAO ESP32-C3 Arduino compilation and existing host alarm/timer tests.
- Assembly STEP reimport and validity checks for all 50 solids.
- Individual production STL roundtrip topology checks.
- Analytic carrier/front-panel versus PCB/component reference intersection tests.
- Gerber ZIP CRC, nine-file layer/drill inventory, README relative links and screenshot checksum checks.

## Scope and outstanding external information

This is a **prepared design-review package**, not a claim that the clock has been printed, assembled, electrically tested or approved for overnight use. The owner reported checking the original CAD; the new compact revision is supported by digital geometry checks only. The firmware still uses safe first-power audio defaults.

The exact source URL, creator and license for the imported MakerWorld shrine and supplied hand-sign artwork remain unconfirmed. Attribution has not been invented. The owner should complete `ATTRIBUTION.md`. Hack Club staff decide whether the disclosed AI assistance and project eligibility meet their rules; file checks cannot guarantee acceptance. No form has been submitted.

The large decorative body remains approximately 339 mm wide. The small-board guidance applies to the PCB; this package does not claim a small case or compatibility with every printer.

## References

Requirements provided by the owner: https://blare.hackclub.com/docs/submitting-your-project

Original PCB-size guidance provided by the owner: https://blare.hackclub.com/docs/pcb-design

Compact native validation: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40623818097

Fresh final-package checks are recorded by the repository's validation workflow. All configured ignored checks and reference-dimension assumptions are retained rather than hidden.
