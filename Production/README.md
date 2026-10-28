# Current compact production files

## PCB

Use **`gerbers.zip`** with the current `../PCB` sources: **95 × 95 mm**, two copper layers, nominal **1.6 mm finished thickness**. The ZIP contains seven Gerber layers and separate plated/non-plated Excellon drill files. It was generated from the native KiCad-validated compact board, not edited by scaling old Gerbers.

`Checks/ERC.rpt`, `DRC.rpt`, and `Drill.rpt` record the source checks and drilling. Configured ignored checks remain visible in the reports. Original 125 × 110 mm manufacturing files are archived separately; do not mix the two sets.

## Printed parts

Print one each of:

- `Case_Parts/Shrine_Body.stl`: revised shrine with the electronics carrier integrated into it.
- `Case_Parts/Front_Panel.stl`: removable face with two key-row openings, display pocket and buzzer vents.
- `Case_Parts/Display_Retainer.stl`: rear screen retaining bar.

Each STL was reloaded and checked for watertightness, consistent winding, zero boundary edges and zero nonmanifold edges. The body is approximately 339 × 339 × 287 mm and requires sufficient printer capacity or a separately designed split. Normal kit keycaps are used; do not print the old tall extensions for this version.

Analytic STEP files for the panel and retainer are included in assembly coordinates. The complete placed clock STEP is `../CAD/JJK_Alarm_Assembly.step`. Print STLs are reoriented to their build planes; the transforms are in `../CAD/Checks/Print_Mesh_Validation.json`.

## Parts and testing

Use four M3 × 8 mm screws, six M3 × 16 mm screws, ten compatible M3 hex nuts, a soft nonconductive display shim and a nylon cable tie. These quantities may require extra parts beyond the kit. Electronics geometry is based on the documented reference envelopes, not measurements of delivered parts.

No PCB or firmware check is a certification for unattended use. The first-power firmware holds the buzzer off pending physical inspection and tests. No fabrication order or Hack Club submission has been made on the owner's behalf.
