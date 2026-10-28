#!/usr/bin/env python3
"""Fill both GND copper zones natively in KiCad before DRC, save exact board."""
import sys
from pathlib import Path
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew

p=Path(__file__).resolve().parents[1]/"PCB/jjkspeakerpcb.kicad_pcb"
board=pcbnew.LoadBoard(str(p))
assert board is not None,"Native board load failed"
zones=list(board.Zones())
assert len(zones)==2,("Expected exactly 2 GND zones",len(zones))
for z in zones:
    assert z.GetNetname() in ("GND","/GND"),z.GetNetname()
    assert z.GetLayer() in (pcbnew.F_Cu,pcbnew.B_Cu),z.GetLayer()
print("Filling",len(zones),"GND zones",flush=True)
filler=pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(str(p),board)
verify=pcbnew.LoadBoard(str(p))
assert verify is not None,"Filled board could not be reloaded"
assert len(list(verify.Zones()))==2
print("NATIVE GND ZONE FILL: board saved and reloaded",flush=True)
