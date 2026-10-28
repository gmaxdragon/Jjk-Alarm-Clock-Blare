# Production files

## PCB

`gerbers.zip` contains the complete validated nine-file KiCad export: front/back copper, front/back solder mask, front/back silkscreen, Edge.Cuts, and separate PTH/NPTH Excellon drills. The PCB circuitry and drilling were not changed by the mechanical-export repair.

Order geometry: **125 x 110 mm**, two copper layers, nominal **1.6 mm finished thickness**. This is not a 100 x 100 mm board. The native board-body STEP in CAD is the dielectric substrate only; use the separately labeled 1.6 mm finished-size envelope for enclosure clearance. Fabrication material, copper weight and finish still need to match the board specification. Native reports retain the ignored-check list.

## Keycaps

`Case_Parts/Keycap_01.step` through `Keycap_06.step` and matching `.stl` files form the six-part set. Each STEP reimports as one valid closed solid, and each STL is watertight with consistent winding. Original dimensions and internal cavity shells are preserved. Each cap is approximately **18.10 x 18.097 x 62.351 mm**.

The source supplied four bodies. Parts 5 and 6 are copies of original bodies 1 and 2. Parts are translated to their own origins for handling, not scaled. The combined `../CAD/Current_References/Six_Keycaps.step` uses a 3-by-2 packing arrangement, not the clock's final button positions. This does not prove stem fit, print orientation, or physical tolerances.

## Enclosure

No print-ready enclosure has been substituted for the user's design. The latest file named `JJK Alarm Clock.stl` actually contains keycaps. The older enclosure is preserved as an open surface reference in `../CAD/Recovered/Enclosure_REFERENCE_ONLY.stl`, outside the production folder.

## Review scope

The owner reports checking CAD fit. No physical power-fault, overnight, or alarm-loudness tests have been recorded. The firmware's first-power configuration holds the buzzer off. Valid source files and manufacturing layers are not a certificate of hardware safety or program acceptance.
