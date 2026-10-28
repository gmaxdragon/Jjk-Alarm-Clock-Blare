# Current mechanical references

- `PCB_Drilled_Body.step`: native KiCad export of the actual drilled **125 x 110 mm** dielectric substrate. Its Z thickness is approximately **1.51 mm** because this export omits copper and solder mask. It is not a populated assembly.
- `PCB_Finished_Size_Envelope.step` and `.stl`: **125 x 110 x 1.6 mm** nominal finished-board sizing reference, using the native substrate geometry with only Z expanded. XY dimensions, drilling positions, and connector/switch spacing are unchanged. This is an enclosure-design envelope, not a separate manufactured PCB or a detailed copper-layer model.
- `Six_Keycaps.step`: six valid solids, in a 3-by-2 packing arrangement for file handling. That packing is NOT a change to the PCB's one-row button layout. Caps 5 and 6 duplicate source bodies 1 and 2.
- `Component_Positions_mm.csv` and `Drill_Positions_mm.csv`: native KiCad coordinates. X is measured from the board's left edge and Y down from its top edge; Edge.Cuts line thickness is excluded.

STEP models are reimported and checked. Do not mistake these references for the required complete assembled-clock STEP. The final enclosure, PCB, TFT and cap placement together is not established by these files.

The electrical PCB is unchanged. Six key centers span 95.25 mm; the supplied 18.10 mm wide caps occupy about 113.35 mm across the row. A new compact layout and matching case, not uniform scaling, are needed to meet the tutorial's under-100-mm guidance without an exception.
