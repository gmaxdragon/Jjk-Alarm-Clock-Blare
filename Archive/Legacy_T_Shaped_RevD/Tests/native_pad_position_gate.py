#!/usr/bin/env python3
"""Native KiCad pad-position parity; blocks wrong back-side mirroring."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew
root=Path(__file__).resolve().parents[1]
board=pcbnew.LoadBoard(str(root/"PCB/jjkspeakerpcb.kicad_pcb"))
assert board is not None,"Native PCB parser failed"
mapping=json.loads((root/"Docs/physical_pad_map.json").read_text())
actual={}
for foot in board.GetFootprints():
    for pad in foot.Pads():
        if not pad.GetNumber():continue
        pt=pad.GetPosition()
        key=(foot.GetReference(),pad.GetNumber())
        assert key not in actual,key
        actual[key]=(pcbnew.ToMM(pt.x),pcbnew.ToMM(pt.y))
expected={}
for p in mapping["pads"]:
    k=(p["ref"],p["number"])
    assert k not in expected,k
    expected[k]=(p["x"],p["y"])
assert set(actual)==set(expected),{"missing":set(expected)-set(actual),"extra":set(actual)-set(expected)}
fails=[(k,ex,actual[k]) for k,ex in expected.items() if math.dist(actual[k],ex)>.015]
assert not fails,{"count":len(fails),"examples":fails[:12]}
print("NATIVE PAD POSITION PARITY PASS:",len(actual),"pads",flush=True)
