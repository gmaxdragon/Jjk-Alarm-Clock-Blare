#!/usr/bin/env python3
"""Native KiCad zone-fill step; never fabricates a board by itself."""
from pathlib import Path
import sys
import pcbnew

if len(sys.argv)!=2:
    raise SystemExit("usage: fill_zones.py PCB/jjkspeakerpcb.kicad_pcb")
filename=Path(sys.argv[1])
board=pcbnew.LoadBoard(str(filename))
if board is None: raise SystemExit("KiCad native PCB file could not be opened")
zones=board.Zones()
print("loaded native KiCad board",board.GetFileName(),"zones",len(zones),"tracks",len(board.GetTracks()))
pcbnew.ZONE_FILLER(board).Fill(zones)
pcbnew.SaveBoard(str(filename),board)
print("KiCad zone fill saved",filename,"size",filename.stat().st_size)
