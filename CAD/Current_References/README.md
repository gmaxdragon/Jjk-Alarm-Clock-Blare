# Current mechanical references

- `PCB_Drilled_Body.step`: native KiCad export of the actual drilled **125 x 110 x 1.6 mm** substrate. It is a PCB body, not a populated assembly. No connectors or component heights are invented.
- `Six_Keycaps.step`: six valid solids, in a 3-by-2 packing arrangement for file handling. That packing arrangement is NOT a change to the PCB's one-row button layout. Caps 5 and 6 duplicate source bodies 1 and 2.
- `Component_Positions_mm.csv` and `Drill_Positions_mm.csv`: coordinates extracted through KiCad's native API. X is measured from the board's left edge and Y down from its top edge.

The mechanical exports are reimported and tested. Do not mistake these references for the required complete assembled-clock STEP. The enclosure, PCB, display and cap positions in the final case are not established by these exports.

No PCB scaling was applied. Its six key centers span 95.25 mm and the uploaded 18.10 mm wide caps occupy about 113.35 mm across the row. A new compact layout, not uniform scaling, is required to satisfy the tutorial's under-100-mm board guidance without an exception.
