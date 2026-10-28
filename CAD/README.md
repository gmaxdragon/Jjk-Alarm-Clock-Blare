# Owner-supplied CAD

`Original_STEP_Exports.zip` preserves the two uploaded STEP files unchanged, including their original names and original coordinates:

- `Alarm Clock Enclosure Step.step`
- `Keycaps.step`

The archive is used because the enclosure STEP alone is 108,873,569 bytes, above GitHub's regular 100 MiB single-file limit. The archive is **not** being called the complete assembled-clock STEP required by BLARE.

The owner reports checking fit in Tinkercad. These checks concern the export files, not a claim that the owner's design work was not done:

- Open Cascade parses the enclosure file but its original assembly root transfers zero shapes.
- The keycap export imports 8,352 individual face shells and no solid. Its imported bounding box is approximately 45.20 x 49.10 x 62.35 mm; this is the entire export, not one keycap.
- The available screenshot shows the case and separate cap-like parts, not the complete PCB/display assembly inside it.

A proposed single-reference repair to the enclosure assembly graph is investigated separately in the audit notes; it must not be treated as an approved solid or combined clock assembly without a successful validation. The original bytes above are retained.

BLARE asks for one complete assembled STEP including PCB and case parts, plus individual case STEP or STL outputs in `Production/`. Those deliverables cannot be honestly manufactured by merely renaming these two source files.

Original shrine geometry includes MakerWorld content. Record the exact creator/model URL and license in `../Docs/ATTRIBUTION.md`.
