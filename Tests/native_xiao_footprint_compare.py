#!/usr/bin/env python3
"""Inspect why the native XIAO matches real pad wiring but not its local library."""
import sys
from pathlib import Path
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew
root=Path(__file__).parents[1]
b=pcbnew.LoadBoard(str(root/"PCB/jjkspeakerpcb.kicad_pcb"))
lib=pcbnew.FootprintLoad(str(root/"PCB/GGK.pretty"),"Seeed_XIAO_ESP32C3_Castellated")
assert b and lib
orig=next(f for f in b.GetFootprints() if f.GetReference()=="U1")
def dump(fp,tag):
    print("FOOTPRINT",tag,"layer",fp.GetLayerName(),
          "position",pcbnew.ToMM(fp.GetPosition().x),pcbnew.ToMM(fp.GetPosition().y),
          "angle",fp.GetOrientationDegrees(),
          "attributes",fp.GetAttributes(),flush=True)
    print("COMPARISON_METHODS", sorted(x for x in dir(fp) if
          "compare" in x.lower() or "equal" in x.lower() or
          "same" in x.lower() or "flip" in x.lower()), flush=True)
    print("BOARD_ITEMS",len(list(fp.GraphicalItems())),"pads",len(list(fp.Pads())),flush=True)
    for p in fp.Pads():
        n=p.GetNumber()
        if n in ("1","8","15","21"):
            pos=p.GetPosition()
            print(tag,"PAD",n,"x",pcbnew.ToMM(pos.x),"y",pcbnew.ToMM(pos.y),
                  "size",pcbnew.ToMM(p.GetSize().x),pcbnew.ToMM(p.GetSize().y),
                  "shape",p.GetShape(),"layers",p.GetLayerSet().FmtHex(),flush=True)
dump(orig,"BOARD")
dump(lib,"LIB_FRONT")
try:
    clone=pcbnew.FootprintLoad(str(root/"PCB/GGK.pretty"),"Seeed_XIAO_ESP32C3_Castellated")
    clone.SetPosition(orig.GetPosition())
    clone.Flip(clone.GetPosition(),False)
    dump(clone,"LIB_FLIPPED")
except Exception as e:
    print("FLIP_FAILURE",type(e).__name__,str(e),flush=True)
