# JJK Alarm CAD

## Original design files

`Original_STEP_Exports.zip` preserves the two owner uploads unchanged:

- `Alarm Clock Enclosure Step.step`
- `Keycaps.step`

The owner reports verifying the fit in Tinkercad. File-conversion checks are separate from that design work. The enclosure source is 108,873,569 bytes, so the originals are archived rather than committed as an oversized single Git file.

## Recovered exports

The reproducible recovery script is `../Tools/recover_cad_exports.py`. It retains the original dimensions and coordinates; it does not change the PCB, invent component placement, or generate screenshots.

| Output | What it contains | Validation |
| --- | --- | --- |
| `Recovered/Keycaps_Recovered.step` | Four original cap bodies, including their internal cavity shells | Sewn at 0.000001 mm; four valid closed solids; reimported and checked |
| `../Production/Case_Parts/Extended_Keycap_01.stl` through `04.stl` | Each original cap as a separate STL | Watertight with consistent winding; original coordinates retained |
| `Recovered/Enclosure_REFERENCE_ONLY.stl` | All 222,961 planar faces recovered from the enclosure export as 264,900 triangles | Reopens with the same dimensions; open seams remain, so this is NOT a print-ready solid |
| `Checks/Export_Recovery.json` | Source hashes, reimport results, sizes and topology checks | Machine-readable evidence |

The keycap export contains four bodies. The PCB has six switches. The complete build needs six caps, so two additional copies are needed after checking the stem fit. An export repair does not prove physical fit.

The enclosure reference measures **340 x 340 x 289.838 mm** in its original coordinate system. Do not scale it to the PCB dimensions: those dimensions describe different parts.

## Complete assembly requirement

The uploaded files do not contain a placed PCB/display assembly. The enclosure reference has **14,489 open boundary edges and 33 edges shared by more than two faces** under the recovery analysis. No holes have been filled and no faces have been deleted to hide those findings.

A complete assembled-clock STEP, including the actual PCB and screen in their intended positions, is still required by the supplied BLARE submission guide. The recovered keycaps and enclosure reference are useful parts of the review package, but are not mislabeled as that entire assembly. Separate top/bottom case parts also cannot be inferred reliably from the uploaded combined surface data.

The original MakerWorld source, creator and license still need to be identified in `../Docs/ATTRIBUTION.md`. Existing supplied screenshots are preserved in `../Docs/Images/`.
