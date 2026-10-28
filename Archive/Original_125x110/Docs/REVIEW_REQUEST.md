# JJK Alarm: review request

**Draft only. This has not been sent or submitted.**

Project: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare

Use the BLARE project/mission in Stardance while signed in: https://stardance.hackclub.com/missions/blare

The BLARE homepage also lists `#blare` and `liam@hackclub.com` for questions. Its legacy design form is closed, and its advertised end date has passed. Ask the organizer about current eligibility rather than assuming that an old form is the correct route.

## Message

Hi Liam,

I'm Vivaan, and this is my JJK Alarm project for BLARE:
https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare

My friend and I worked on the PCB and schematic. I modified the case in Tinkercad using a MakerWorld shrine model. The README explains the design and includes my actual screenshots, the BOM, and an honest AI-assistance disclosure. AI helped me with ideas, debugging, firmware, and organizing the documentation. The README story came from my voice-typed explanation.

The electronics pass the recorded native KiCad ERC/DRC checks, and the ESP32-C3 firmware compiles. The repository has the PCB source files, firmware, and complete Gerbers. I checked fit in my CAD, but the converted enclosure file still needs a clean complete-assembly export containing the PCB and screen. The keycap STEP was recovered into four valid solids and individual STL files; the original exports are also preserved. I am not claiming the clock has already been built or tested.

Could you confirm whether I can still submit through Stardance, whether the 125 x 110 mm PCB can be accepted despite the tutorial's under-100 mm guidance, and whether my disclosed use of AI is acceptable? I understand the completed assembly export and exact MakerWorld credit still need to be supplied before those requirements can be marked complete.

I also forgot to click Publish to Stardance for some PCB/schematic timelapses. I selected Public, so I am not sure they were attached. I have not claimed unverified recording hours.

Thank you for reviewing it.

Vivaan

## Current file map

- `README.md`: personal project description, original screenshots, BOM, disclosures.
- `PCB/`: unchanged current KiCad project, schematic and layout.
- `Firmware/JJK_Alarm/`: Arduino firmware and user-supplied hand-sign bitmap.
- `Production/gerbers.zip`: full PCB manufacturing layer/drill set.
- `Production/Case_Parts/`: recovered individual keycap STL files.
- `CAD/Recovered/Keycaps_Recovered.step`: four validated solids.
- `CAD/Recovered/Enclosure_REFERENCE_ONLY.stl`: recoverable enclosure geometry, not a closed print model.
- `CAD/Checks/Export_Recovery.json`: measured CAD recovery results.
- `Docs/SUBMISSION_CHECK.md`: exact remaining requirements, without hiding exceptions.
