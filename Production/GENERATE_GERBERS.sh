#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

BOARD="PCB/jjkspeakerpcb.kicad_pcb"
SCH="PCB/jjkspeakerpcb.kicad_sch"
OUT="Production/ReviewOnly"
RAW="$OUT/gerbers"
mkdir -p "$RAW"
rm -f "$RAW"/* "$OUT/gerbers.zip" "$OUT/native_erc.rpt" "$OUT/native_drc.rpt" "$OUT/drill_report.rpt"

echo "Using $(kicad-cli version)"
echo "Running KiCad 10 ERC (latest submitted rectangular schematic)"
kicad-cli sch erc --severity-all --exit-code-violations -o "$OUT/native_erc.rpt" "$SCH"

echo "Running KiCad 10 DRC with netlist parity and refilled zones"
kicad-cli pcb drc --severity-all --schematic-parity --refill-zones --exit-code-violations -o "$OUT/native_drc.rpt" "$BOARD"

echo "Plotting individual fabrication layers"
kicad-cli pcb export gerbers --check-zones --no-protel-ext -l 'F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts' -o "$RAW" "$BOARD"

echo "Exporting Excellon plated and non-plated drill files"
kicad-cli pcb export drill --format excellon --drill-origin absolute --excellon-units mm --excellon-separate-th --generate-report --report-path "$OUT/drill_report.rpt" -o "$RAW" "$BOARD"

python3 - <<'PY'
from pathlib import Path
import zipfile, sys, re
out=Path("Production/ReviewOnly")
raw=out/"gerbers"
need=["F_Cu","B_Cu","F_Mask","B_Mask","F_Silkscreen","B_Silkscreen","Edge_Cuts"]
gerbs={name: next((p for p in raw.glob("*.gbr") if name.lower() in p.stem.lower()), None) for name in need}
for name,f in gerbs.items():
    if f is None or f.stat().st_size < 100:
        raise SystemExit(f"Missing or empty Gerber layer: {name}")
    t=f.read_text(errors="replace")
    if "M02*" not in t:
        raise SystemExit(f"Gerber file missing EOF: {f}")
drills=list(raw.glob("*.drl"))
if not drills:
    raise SystemExit("No Excellon drill files")
for d in drills:
    t=d.read_text(errors="replace")
    if "M48" not in t:
        raise SystemExit(f"Invalid drill header: {d.name}")
    if "X" not in t or "Y" not in t:
        raise SystemExit(f"No drill coordinates in {d.name}")
report=(out/"drill_report.rpt").read_text(errors="replace")
if not report.strip():
    raise SystemExit("Empty drill report")
zip_path=out/"gerbers.zip"
with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
    for file in sorted(raw.glob("*")):
        if file.is_file() and file.suffix.lower() in (".gbr",".drl"):
            z.write(file,arcname=file.name)
with zipfile.ZipFile(zip_path) as z:
    if z.testzip() is not None:
        raise SystemExit("ZIP corruption found")
    n=z.namelist()
    if len(n)<9: # 7 Gerber + at least two drill files
        raise SystemExit(f"Incomplete Gerber package: {n}")
print(f"Completed review-only Gerber ZIP: {zip_path}, {len(n)} manufacturing layers/drill files")
PY
