# JJK Alarm CAD

## Corrected exports

`JJK_Alarm_Corrected_Parts.zip` collects the checked mechanical references and six keycap parts. Individual files are also committed.

| File | Contents |
| --- | --- |
| `Current_References/PCB_Drilled_Body.step` | Native KiCad export of the current 125 x 110 mm drilled substrate, approximately 1.51 mm thick without copper/mask |
| `Current_References/PCB_Finished_Size_Envelope.step` and `.stl` | Nominal 125 x 110 x 1.6 mm finished-board reference with the same XY and holes; Z-only envelope expansion is documented |
| `Current_References/Six_Keycaps.step` | Six reimport-tested closed solids; caps 5 and 6 repeat original bodies 1 and 2 |
| `../Production/Case_Parts/Keycap_01.step` through `Keycap_06.step` | One valid solid per file |
| `../Production/Case_Parts/Keycap_01.stl` through `Keycap_06.stl` | Six watertight, consistently wound meshes; geometry not rescaled |
| `Current_References/Component_Positions_mm.csv` | Component origins, not necessarily body centers |
| `Current_References/Drill_Positions_mm.csv` | Actual drill centers and diameters, including mounting holes and vias |
| `Checks/Native_PCB_Dimensions.json` | Native measurement evidence |
| `Checks/Current_Mechanical_Exports.json` | STEP reimport, dimensions, keycap counts and STL checks |

The keycap pack is arranged 3 by 2 only for export handling. The PCB still has one row of six switches at 19.05 mm pitch. The printed caps are approximately 18.10 x 18.097 x 62.351 mm each. Copies do not change the switch-stem design. Physical fit remains distinct from file validity.

## Latest STL upload finding

`Checks/Latest_STL_Uploads.json` records the two latest uploads, `JJK Alarm Clock.stl` and `Keycaps.stl`. Both are 417,684-byte files with 8,352 triangles and the same four-keycap geometry at different positions. Neither includes the shrine enclosure. The combined keycap set is approximately 45.20 x 49.097 x 62.351 mm. A filename alone does not establish that an enclosure was exported.

## Original sources and enclosure

`Original_STEP_Exports.zip` preserves the owner's earlier `Alarm Clock Enclosure Step.step` and `Keycaps.step` unchanged. The original keycap source was sewn into four valid solids with its inner cavity shells preserved; it remains in `Recovered/Keycaps_Recovered.step`. Earlier four-part STL exports are archived in `Recovered/Original_Keycap_STL` after the new six-part set is generated.

`Recovered/Enclosure_REFERENCE_ONLY.stl` recovers all 222,961 source planar faces as 264,900 triangles. It measures 340 x 340 x 289.838 mm in the original coordinate system. It still has 14,489 open boundary edges and 33 nonmanifold edges under the prior analysis. It is not a closed printable solid. No arbitrary hole filling, dimensional scaling, smoothing or invented case split is claimed.

The owner reports verifying fit in Tinkercad. The remaining issue is the exported data: neither the new keycap-only STLs nor the recovered open enclosure includes the PCB/display placed in a complete assembly. A valid whole-enclosure export and assembled-clock STEP are still needed. Do not rename a keycap file or open reference as the complete clock.

## PCB size

The correct finished board size is **125 x 110 x 1.6 mm**. The native drawing bounding box is slightly larger because it includes the Edge.Cuts pen width; the actual routed size uses the line center. The component and drill tables use that actual outline. The BLARE tutorial's under-100-mm guidance is not met by this layout. Uniformly shrinking it would alter connector pitch, switch spacing and holes. No compact PCB redesign or organizer exception is claimed.
