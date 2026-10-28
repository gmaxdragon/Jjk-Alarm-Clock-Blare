# Rectangular BLARE work-in-progress snapshot

Date: 2026-10-26 (Pacific)

This branch preserves the latest **user-supplied** rectangular BLARE circuit and PCB instead of the older T-shaped Rev D shown in the root README on main.

- Source: `PCB/jjkspeakerpcb.kicad_pro`, `.kicad_sch`, `.kicad_pcb` from the user’s most recent uploads. Original KiCad filenames were suffixed by the chat uploader and have been normalized here to the matching project basename.
- Reference screenshots: `Docs/Images/PCB_Layout_2026-10-26.png` and `Docs/Images/Schematic_2026-10-26.png`.
- `Production/Incomplete_Gerbers/` stores only five supplied Gerber layers as **evidence**, not a fabrication-ready release. This upload did **not** include drill files, solder-mask layers, or a completed `gerbers.zip`.
- `CAD/` is awaiting the user's Tinkercad enclosure and an assembled STEP file.
- `Firmware/` is inherited from the older Rev D and has **not** been confirmed to match the rectangular board. Do not assume it is ready to flash.
- The existing root `README.md` is intentionally **unchanged**, at the user's explicit request. The user's personal revised README is pending their approval and is preserved separately in their ChatGPT Library.

**NOT READY FOR FABRICATION OR SUBMISSION.** Electrical verification, firmware integration, physical part fit, case CAD, and complete production outputs remain to be finished. User-reported DRC passes are not an independent manufactured-device certification.
