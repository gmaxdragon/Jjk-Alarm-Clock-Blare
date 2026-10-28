# JJK Alarm compact CAD

## The complete assembly

`JJK_Alarm_Assembly.step` contains the complete placed compact design, including all three case parts, the drilled 95 × 95 mm board, component reference envelopes and fastener references. It is a genuine AP214 faceted BREP in millimeters, not a renamed STL. Reimport recovered **50 valid solids**. Coplanar triangles were consolidated into polygonal planar faces without scaling the geometry.

The sculptural source was nonmanifold. The revised decorative body was solidified using a 1 mm voxel grid and a 3-cell closing operation, then functional mounting geometry was added. Small decorative details and tips can change. The exact owner upload is preserved in `Owner_Originals/JJK_Alarm_Clock_Enclosure.stl`; it is not replaced by the repaired version. The original rectangular design and tall keycaps are preserved in `../Archive/Original_125x110`.

## Current files

- `JJK_Alarm_Assembly.step`: complete placed model.
- `Reference/PCB_Substrate.step`: native KiCad substrate export. Its 1.51 mm dielectric thickness excludes copper/mask.
- `Reference/PCB_Finished_Envelope.step`: same XY and drill positions, expanded only through thickness to the nominal 1.6 mm finished-board envelope.
- `Reference/Body_Mesh.npz`: indexed source of the checked revised faceted body.
- `Checks/Assembly_STEP_Validation.json`: STEP reimport, part counts and solid validity.
- `Checks/Print_Mesh_Validation.json`: actual print STL reimport checks and placement transforms.
- `Checks/Mechanical_Report.json`: design dimensions and component-versus-carrier/panel intersection checks.

The exact analytic front-panel and retainer STEP files are also in `../Production/Case_Parts`. The shrine print file is STL. The BLARE instructions supplied by the owner allow STL for individual production parts.

## Dimensions and coordinate system

All values below are design dimensions, not measurements of received hardware.

| Item | Dimension / location |
| --- | --- |
| PCB | 95 × 95 × 1.6 mm finished envelope |
| PCB mounting-hole centers, from board top-left | (5,5), (90,5), (5,90), (90,90) mm |
| PCB mounting-hole diameter | 3.2 mm |
| Switch centers, top row from board top-left | (28.45,60), (47.5,60), (66.55,60) mm |
| Switch centers, bottom row | (28.45,82), (47.5,82), (66.55,82) mm |
| Horizontal / vertical pitch | 19.05 / 22 mm |
| Front-panel body | 106 × 180 mm face, 3 mm base thickness; rear features increase overall depth |
| Each key-row aperture | 57 × 20.2 mm; 1.8 mm rib between rows |
| Modelled normal keycaps | 18.1 × 18.1 × 8.5 mm envelopes |
| TFT module reference | 21.08 × 73.15 × 3.7 mm |
| TFT viewing window | 18 × 62 mm |
| Display pocket side clearance | 0.5 mm per side against the reference module |
| Retainer rear gap / shim allowance | 0.5 mm |
| Printed M3 clearance holes | 3.4 mm |
| Nut pockets | Approximately 5.976 mm across flats for nominal 5.5 mm M3 nuts |
| USB-cable exit passage | 18 × 12 mm |
| Buzzer vents | Nine 1.7 mm holes on a 3 mm grid |
| Sculptural body | Approximately 339 × 339 × 287 mm; no uniform scale reduction |

Assembly coordinates use X across the clock, negative Y toward the front, and Z upward. The PCB front is at Y=103 mm, with board bounds X=125.5..220.5 and Z=46..141 mm. The TFT is above the PCB. The two-row key layout is UP/TIME/SNOOZE above DOWN/CLOCK/ALARM.

The TFT and other electronics are clearance models, not exact supplier CAD. The parts must be checked when received. Clearance models and software intersection tests do not establish switch travel forces, solder-joint height or cable bend radius.

## Assembly order

1. Inspect/finish the three printed parts and clear the cable passage and nut pockets. The shrine requires a large enough printer; the included file is not pre-split for a smaller build volume.
2. Insert four M3 nuts through the side-entry slots in the PCB support posts. Their openings are accessible from the electronics cavity before fitting the board.
3. Route the USB cable through the back passage. Fit a nylon zip tie through the integral saddle for strain relief without crushing the cable.
4. Attach the populated board to its four posts using four M3 × 8 mm screws. Keep the screw heads inside the board's copper keepout regions. Do not let solder tails touch the case or fasteners.
5. Wire the TFT by its printed pin labels. Seat it in the front-panel pocket. Place a soft nonconductive shim in the retainer gap, fit the retainer, and use two M3 × 16 mm screws and nuts. Do not clamp the LCD glass hard.
6. Fit the front panel using four more M3 × 16 mm screws and captive nuts. Ensure all wiring remains inside and is not pinched.
7. Fit the six normal kit keycaps. Check free travel, including at full depression. The original tall cap extensions are not intended for this panel.
8. Perform supervised electrical first-power and firmware tests before relying on the alarm. The audio remains disabled in the first-power firmware configuration.

`Print_Mesh_Validation.json` records rigid transforms used to orient the print STLs. The full STEP retains assembly coordinates. The body has its base at Z=0 in the print STL; the panel and retainer are placed flat. Use appropriate supports and material/process settings for the sculptural overhangs. Watertightness is a geometry check, not a guarantee of print success.
