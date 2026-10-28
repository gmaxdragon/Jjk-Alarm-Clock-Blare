# JJK Alarm submission check

## Scope

Current design: the owner's rectangular 125 x 110 mm PCB and six-switch row. The earlier T-shaped Rev D generators and documentation are archived and are not current fabrication sources.

The owner reports verifying CAD fit. This report distinguishes that statement from whether the uploaded files meet the required delivery format. No physical hardware test is inferred from a screenshot or a software build.

## Completed file work

- Full owner-narrated README, project story, design decisions, challenges, firmware explanation, BOM, AI disclosure, Stardance note, future improvements.
- Original supplied CAD, PCB layout, PCB 3D, schematic, overview and artwork images. Original byte checksums are kept; no new project images were generated.
- Current matching KiCad `.kicad_pro`, `.kicad_sch` and `.kicad_pcb`.
- Firmware and artwork, real ESP32-C3 compile checks, alarm/timer host tests.
- Complete `Production/gerbers.zip`: seven Gerber layers plus PTH/NPTH drill files. ZIP CRC and required-layer inventory checked.
- Native ERC and DRC reports retained, including the configured ignored-check lists.

## Remaining items that cannot be certified from the current files

1. **Complete assembly STEP export.** The supplied `Alarm Clock Enclosure Step.step` is a 108,873,569-byte faceted conversion. Its original assembly representation imports zero geometry through Open Cascade despite parsing as STEP. `Keycaps.step` imports surfaces, not closed solids. A correctly exported entire clock assembly including PCB, screen and case parts is still not established. This is an export/deliverable issue, not a denial of the owner's CAD fit check.
2. **Separate printable case parts.** The required per-part production exports must be known to load correctly and retain the intended fit; conversion attempts and original files must not be passed off as approved manufacturing outputs.
3. **Board size.** The supplied BLARE PCB tutorial says to keep both dimensions under 100 mm. The current PCB is 125 x 110 mm. The earlier assistant selected this larger size. Do not shrink the design silently: six keys at 19.05 mm pitch require a layout/CAD change to meet that guidance. Obtain a program exception or revise the design before claiming size compliance.
4. **Source credits.** Exact MakerWorld model link, creator and license are missing. The source/usage permission for the supplied hand-sign artwork is also not recorded. No source has been invented.
5. **AI acceptance.** The README records the owner's spoken story and accurately discloses AI help. A BLARE organizer's public review says that AI must not be used in the README; disclose the assistance and get a ruling rather than promise acceptance. Generic Stardance percentage claims are not treated as a verified BLARE-specific allowance.
6. **Complete assembly image.** The user supplied a case view, PCB views and a desktop collage. They are all preserved. None is labeled as a physical completed clock or as a verified PCB-inside-case cutaway when it does not show that.

## Sources

- Owner-supplied BLARE submission instructions: https://blare.hackclub.com/docs/submitting-your-project
- Owner-supplied BLARE PCB tutorial, including the under-100-mm instruction: https://blare.hackclub.com/docs/pcb-design
- BLARE organizer's public review about complete assembly STEP and README AI use: https://stardance.hackclub.com/projects/62645
- Prior native KiCad run: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40441400924
- Latest artwork/name ESP32 compile run before packaging: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40601357396

**Status: README and electronic-source package prepared; remaining CAD/export, size and attribution/program-acceptance items must not be labeled complete without evidence.**
