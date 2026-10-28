# JJK Alarm submission check

## Current package

This is the owner's rectangular **125 x 110 mm** JJK Alarm, not the archived T-shaped design. The owner reports verifying CAD fit. No screenshot, CAD inspection, or software build is presented as a physical hardware test.

## Finished

- Published owner-narrated README, design choices, challenges, circuit/firmware explanation, BOM, AI disclosure, Stardance note and planned upgrades.
- Original supplied screenshots and artwork, with byte-checksum provenance. No generated project renders were added.
- Matching KiCad `.kicad_pro`, `.kicad_sch` and `.kicad_pcb` sources.
- Arduino firmware, portrait image, ESP32-C3 compilation and host alarm/timer tests.
- Complete `Production/gerbers.zip`, containing seven Gerber layers plus PTH and NPTH drill files.
- Native ERC/DRC reports, retaining their configured ignored-check lists.
- **Keycap export repaired:** four closed, valid solids, a successfully reimported combined STEP, and four separate watertight STL part files. Original inner cavity shells, dimensions and coordinates retained.
- **Enclosure geometry recovered:** all 222,961 supplied planar faces converted into an importable reference STL, with no missing faces, scaling, smoothing or hole filling. The reference is explicitly not a print-ready solid.
- Reproducible recovery script and machine-readable results in `CAD/Checks/Export_Recovery.json`.

## Remaining deliverable, not a repeated request to recheck the design

**A valid complete-clock assembly export.** The original enclosure's assembly reference does not import normally. Its recovered geometry still has 14,489 open boundary edges and 33 edges shared by more than two faces. The files also do not establish the PCB and TFT placement within the case. Therefore no output is falsely named the fully assembled clock STEP. Individual top/bottom case parts and a genuine assembled-fit screenshot remain absent. The supplied keycap source has four bodies for a six-switch PCB, so the build requires two additional copies after a stem-fit test.

The next useful source is a direct Tinkercad export of the actual whole assembly, including the PCB/display reference objects, or the original design link. Merely renaming an STL to STEP does not satisfy this requirement. This is about file content and export integrity, not a denial of the owner's reported fit check.

## Reviewer decisions and credits

- **Board size:** the supplied BLARE PCB tutorial says both dimensions should be under 100 mm. The earlier assistant selected 125 x 110 mm. Keep the finished design unchanged and request an exception; do not silently shrink the six-key layout.
- **AI disclosure:** preserve the owner's honest disclosure. A public BLARE organizer review says AI must not be used in the README. The user supplied the spoken story, and AI organized/edited it and wrote substantial firmware. Acceptance must be decided by the organizer, not claimed by this repository.
- **Source credits:** the exact MakerWorld model URL, creator and license, plus the hand-sign artwork source, remain unconfirmed. Search did not establish a reliable match. No candidate has been presented as proven attribution.
- **Submission route:** the old linked BLARE design form displays “This form is closed.” The current site directs designs to Stardance and a BLARE mission page exists. The homepage still lists September 30, 2026 as its end date, so ongoing eligibility needs organizer confirmation rather than an assumed deadline extension.

A prepared message with the repository link is in `REVIEW_REQUEST.md`. It is a draft, not an email or form submission.

## Evidence and sources

- Submission guide supplied by the owner: https://blare.hackclub.com/docs/submitting-your-project
- PCB tutorial supplied by the owner: https://blare.hackclub.com/docs/pcb-design
- Main-branch source/build checks: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40606564625
- CAD recovery and reimport checks: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40613420021
- Organizer's public review: https://stardance.hackclub.com/projects/62645
- BLARE homepage: https://blare.hackclub.com/
- Stardance mission: https://stardance.hackclub.com/missions/blare
- Legacy design form checked: https://forms.hackclub.com/t/gRWUubQat3us

**Status: organized design-review package prepared; full submission compliance and funding approval are not claimed. No submission has been sent on the owner's behalf.**
