#!/usr/bin/env python3
"""Bundle local footprints/symbols so the native GGK KiCad source is editable.

This does NOT certify manufacturability, electrical design, or physical keycap fit.
The board is routed by build_board.py and validated separately.
"""
from __future__ import annotations
import os,re,json,runpy
from pathlib import Path
BASE=Path(__file__).parent
BOARD=BASE/'PCB'
PCB=BOARD/'jjkspeakerpcb.kicad_pcb'
SCH=BOARD/'jjkspeakerpcb.kicad_sch'
assert PCB.exists() and SCH.exists()
# Avoid running generator here (no stale output); reuse embedded board footprints.
b=PCB.read_text()
s=SCH.read_text()

def balanced(text,pos):
    if text[pos]!='(':raise ValueError('start on parenthesis')
    depth=0; string=False; slash=False
    for i in range(pos,len(text)):
        c=text[i]
        if string:
            if slash:slash=False
            elif c=='\\':slash=True
            elif c=='"':string=False
            continue
        if c=='"':string=True
        elif c=='(':depth+=1
        elif c==')':
            depth-=1
            if depth==0:return text[pos:i+1]
    raise ValueError('unterminated s-expression')

lib_dir=BOARD/'GGK.pretty';lib_dir.mkdir(exist_ok=True)
footprints={}
for m in re.finditer(r'\(footprint "GGK:([^"]+)"',b):
    lib=m.group(1)
    if lib in footprints:continue
    t=balanced(b,m.start())
    # Convert board-instance attributes into a reusable, front-side native footprint.
    t=re.sub(r'^\(footprint "GGK:[^"]+" \(layer "[FB]\.Cu"\) \(uuid "[^"]+"\) \(at [^)]+\) \(attr ([^)]+)\)',
        lambda m:'(footprint "'+lib+'" (version 20221018) (generator pcbnew) (layer "F.Cu") (attr '+m.group(1)+')',t,count=1)
    t=t.replace('"B.Cu"','"F.Cu"').replace('"B.Paste"','"F.Paste"').replace('"B.Mask"','"F.Mask"')
    t=t.replace('"B.Fab"','"F.Fab"').replace('"B.SilkS"','"F.SilkS"').replace('"B.CrtYd"','"F.CrtYd"')
    # Canonical XIAO front-view library: reflect B-side local X back to
    # the original Seeed front-view coordinate system. The board's physical
    # U1 instance remains on B, and KiCad owns the back-layer flip.
    # U1 has a custom native BACK-mounted pattern with 22 documented
    # castellated/underside pads. Preserve this footprint's B-side layers
    # in the project-local library so KiCad compares the *actual* pattern.
    if lib == 'Seeed_XIAO_ESP32C3_Castellated':
        for suffix in ('Cu','Paste','Mask','Fab','SilkS','CrtYd'):
            t=t.replace('"F.'+suffix+'"','"B.'+suffix+'"')
    t=re.sub(r'\(path "/[^"]+"\)', '', t)
    t=re.sub(r'\(net \d+ "[^"]+"\)', '', t)
    (lib_dir/(lib+'.kicad_mod')).write_text(t+'\n')
    footprints[lib]=t

# Symbol library: split out exact embedded symbol definitions.
a=s.index('(lib_symbols')
library_block=balanced(s,a)
syms=[]
for m in re.finditer(r'\(symbol "GGK:([^\"]+)"',library_block):
    x=balanced(library_block,m.start())
    name=m.group(1)
    x=x.replace('(symbol "GGK:'+name+'"', '(symbol "'+name+'"',1)
    syms.append(x)
(BOARD/'GGK.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+'\n'.join(syms)+'\n)\n')
(BOARD/'sym-lib-table').write_text('(sym_lib_table\n  (lib (name "GGK") (type "KiCad") (uri "${KIPRJMOD}/GGK.kicad_sym") (options "") (descr "Bundled GGK alarm components"))\n)\n')
(BOARD/'fp-lib-table').write_text('(fp_lib_table\n  (lib (name "GGK") (type "KiCad") (uri "${KIPRJMOD}/GGK.pretty") (options "") (descr "Bundled GGK PCB footprints"))\n)\n')
print(json.dumps({'native_footprints':list(footprints),'embedded_schematic_symbols':len(syms),'footprint_bytes':sum(len(x) for x in footprints.values())},indent=2))
