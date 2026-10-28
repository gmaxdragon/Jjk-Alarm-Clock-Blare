# Compact build acceptance record

The owner confirmed on October 27, 2026 that their printer fits the 339 × 339 × 287 mm body. Printer envelope is resolved. No split is required for that printer.

## Verified digital evidence

- Native compact PCB: 95 × 95 mm; original 125 × 110 mm preserved.
- Fresh native ERC: zero violations. DRC: zero violations, zero unconnected items, zero schematic parity issues, under the project's documented check settings.
- Package checker: preserved original hashes, electrical pad-net map, Gerber outline/inventory/CRC, linked assets and validated STEP/STL hashes pass.
- Independent STL edge analysis: all three production files have zero open, nonmanifold or inconsistently oriented edges and zero degenerate triangles.
- All 64 switch combinations pass the independent directed PCB diode-connectivity model in Tests/matrix_circuit_test.py. This does not execute the ESP32's real electrical inputs.
- Firmware compilation and alarm/timer host tests are checked by the repository workflow. Read the run for the exact final commit before reporting its result.

## Physical acceptance record — results still required

Leave each item pending until its result is observed. A reference model, successful compile or software flag does not count as a physical result.

| Test | Required observation | Current result |
| --- | --- | --- |
| Purchased parts | Display outer dimensions and connector, buzzer dimensions/current/type/polarity, XIAO sockets, switches and keycaps agree with the documented envelopes | Pending |
| Sliced print | All three files fit the confirmed printer; slice preview shows continuous mounts, nut slots, cable tunnel and a suitable support strategy | Pending |
| Case assembly | Four PCB screws and six panel/retainer screws engage their nuts; no solder tails touch fasteners; panel can be fitted and removed | Pending |
| Button motion | All six fitted caps move fully and return freely with the panel installed | Pending |
| Cable route | Actual USB plug seats fully; TFT wires and USB cable reach without strain, pinching or obstructing controls | Pending |
| Display | Correct labelled J3 wiring, portrait image/time visible and unclipped; retainer holds module without pressure on glass | Pending |
| Matrix | At 115200 baud, each physical key produces its named event once per press; hold and release work; combinations do not create phantom events | Pending |
| Reset/boot | Normal reset and upload work with keys released; inspect behavior while each key is held; GPIO8/9 strap behavior must be verified on the real XIAO | Pending |
| Buzzer driver | Verify actual Q1 pinout and buzzer current/polarity/type; first-power flags remain zero until inspected; supervised tone test succeeds after verification | Pending |
| Clock/alarm | Manual setting, NTP, weekday selection, enable/disable, ring, five-minute snooze and dismissal work on the assembled device | Pending |
| Timing/UI | Countdown, stopwatch, short/long controls and settings persistence behave correctly | Pending |
| Restart | Power cycle preserves intended settings; clock is manually set or resynchronizes; no claim of timekeeping during a power loss | Pending |
| Credits | Exact MakerWorld shrine and supplied artwork creator/source/license are recorded in ATTRIBUTION.md | Pending |

The saved analytic collision test is limited to the carrier/front panel versus PCB/component reference models. It does not verify every complete-body interface, insertion path, cable bend radius, actual switch travel or manufacturing tolerance.

No fabrication order, physical test result, source license or organizer approval has been inferred. This record supports technical review; it does not mark the project production-ready.
