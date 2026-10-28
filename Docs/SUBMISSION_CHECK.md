# JJK Alarm submission check

## Current design

This is the owner's rectangular **125 x 110 mm** JJK Alarm. The owner reports checking CAD fit. The latest updates repair file exports and documentation, not the electrical layout. Neither physical testing nor program acceptance is implied.

## Prepared and checked

- Owner-narrated README, personal story, screenshots, BOM, AI disclosure, Stardance note and the requested note about later PCB changes.
- Original screenshot/artwork files and their byte-checksum manifest. No generated project render is used as a photo or CAD evidence.
- Matching native KiCad project, schematic and PCB. The actual size is measured from Edge.Cuts centerline coordinates, excluding the drawing's stroke width.
- Real ESP32-C3 firmware compile and alarm/timer tests, portrait hand-sign image above the stacked time.
- Complete `Production/gerbers.zip`: seven Gerber layers plus PTH and NPTH drills, unchanged by the CAD repairs.
- Fresh native KiCad ERC/DRC with schematic parity and ground-zone refill. Reports retain configured ignored-check lists.
- Native drilled PCB substrate STEP and a separately labeled 125 x 110 x 1.6 mm finished-size envelope. The native substrate is approximately 1.51 mm without copper/mask; the enclosure envelope is not mislabeled as a detailed layer model.
- Six closed keycap STEP solids, six separate watertight STL parts, successful STEP reimports and exact dimension tables. Two extra caps are copies of two of the four supplied bodies; no shape scaling was applied.
- Machine-readable checks in `CAD/Checks`; repeatable export scripts in `Tools`.

## Specific unresolved export

**The complete clock assembly is not present in the available exports.** Both latest uploads, including the one named `JJK Alarm Clock.stl`, contain the same four-keycap set at different positions. The old enclosure reference remains an open surface, with 14,489 boundary edges and 33 nonmanifold edges in its recovery report. It cannot be honestly relabeled a finished printable enclosure or a full assembly containing the PCB and TFT.

The missing source is an export of the actual whole enclosure/assembly from the owner's CAD document, not another export of the selected keycaps. Separate printable case sections and a genuine assembled-fit view must correspond to that geometry. The owner's CAD fit check is preserved as owner-reported evidence; this is a file-content issue.

## Size and organizer decisions

The PCB remains **125 x 110 mm**, so it does not satisfy the supplied tutorial's under-100-mm board guidance. Its six switch centers span 95.25 mm and the supplied 18.10 mm caps span about 113.35 mm across the row. Uniform scaling would break component pitch and holes. A compact layout, such as two rows of three switches, would also change the case openings. Otherwise an organizer must approve the larger board. No exception is assumed.

Keep the honest AI-assistance disclosure. Program staff decide whether the amount of AI assistance is accepted. Do not infer that disclosure guarantees eligibility. The original MakerWorld model URL, creator and license and the source of the supplied artwork still need to be recorded in `ATTRIBUTION.md`; no guessed creator is asserted.

The old linked submission form was previously observed closed. Current submission route and eligibility are organizer decisions. No submission or message has been sent on the owner's behalf.

## Sources and evidence

- Owner-supplied requirements: https://blare.hackclub.com/docs/submitting-your-project
- Owner-supplied PCB tutorial: https://blare.hackclub.com/docs/pcb-design
- Original CAD recovery run: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40613420021
- Fresh source and firmware checks: https://github.com/gmaxdragon/Jjk-Alarm-Clock-Blare/actions/runs/40619542440
- New mechanical export evidence: `CAD/Checks/Current_Mechanical_Exports.json` and `CAD/Checks/Native_PCB_Dimensions.json`

**Status: organized and tested design-review files; complete-assembly export and full submission compliance are not claimed.**
