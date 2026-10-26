#!/usr/bin/env python3
"""Independent Rev C solder-copper connectivity check (does not use KiCad).

A positive result is a supplemental mathematical/layout check. KiCad native ERC,
zone fill, DRC, Gerber inspection and physical testing remain mandatory.
"""
from __future__ import annotations
import json,runpy,collections,math
from pathlib import Path
from shapely.geometry import Point,box,LineString
from shapely.strtree import STRtree

root=Path(__file__).resolve().parents[1]
src=runpy.run_path(str(root/'build_board.py'))
pads=src['PADS']; segments=src['segments']; vias=src['vias']; poly=src['POLY']
objects=[]; bynet=collections.defaultdict(list); padkeys=collections.defaultdict(list)

def add(net,layer,geom,label,key=None,bridge=None):
    idx=len(objects)
    obj={'net':net,'layer':layer,'geom':geom,'label':label,'key':key,'bridge':bridge}
    objects.append(obj); bynet[net].append(idx)
    if key is not None:padkeys[net].append((key,idx))
for q in pads:
    if not q['net'] or q['role']=='np_thru_hole':continue
    x,y=q['at']
    if isinstance(q['size'],tuple):
        w,h=q['size'];shape=box(x-w/2,y-h/2,x+w/2,y+h/2)
    else:shape=Point(x,y).buffer(q['size']/2, resolution=40)
    key=q['part']+':'+q['number']
    layers=[1] if q['role']=='smd' else [0,1]
    for l in layers:add(q['net'],l,shape,'PAD '+key,key=key,bridge=key if len(layers)==2 else None)
for j,(a,b,layer,net) in enumerate(segments):
    g=LineString([a,b]).buffer(.125, cap_style=1)
    add(net,0 if layer=='F.Cu' else 1,g,'TRACK '+str(j))
for j,(p,net) in enumerate(vias):
    for l in [0,1]:add(net,l,Point(p).buffer(.35, resolution=32),'VIA '+str(j),bridge='VIA_'+str(j))

parent=list(range(len(objects)))
def find(x):
    while parent[x]!=x:
        parent[x]=parent[parent[x]];x=parent[x]
    return x
def union(a,b):parent[find(a)]=find(b)

for net,ids in bynet.items():
    # Plated through-hole pads and each via bridge their front/back geometry.
    bridges=collections.defaultdict(list)
    for i in ids:
        if objects[i]['bridge']:bridges[objects[i]['bridge']].append(i)
    for group in bridges.values():
        for j in group[1:]:union(group[0],j)
    for layer in (0,1):
        active=[i for i in ids if objects[i]['layer']==layer]
        geoms=[objects[i]['geom'] for i in active]
        tree=STRtree(geoms)
        for local_i,g in enumerate(geoms):
            for other in tree.query(g):
                j=int(other)
                if j<=local_i:continue
                if g.intersects(geoms[j]) or g.distance(geoms[j])<=.005:
                    union(active[local_i],active[j])

def check():
    lost={}
    for net,pad_list in padkeys.items():
        bypad=collections.defaultdict(list)
        for key,i in pad_list:bypad[key].append(i)
        groups=collections.defaultdict(set)
        for key,idxs in bypad.items():groups[find(idxs[0])].add(key)
        if len(groups)>1:lost[net]=list(groups.values())
    return lost
lost=check()
result={'source':'Native KiCad PCB generated from Rev C source; math connectivity check independent from router report',
        'n_pads':len(padkeys),'n_conductor_shapes':len(objects),
        'trace_segments':len(segments),'vias':len(vias),
        'net_count':len(bynet),'unconnected_net_groups':lost,
        'zero_unrouted_pad_networks':not bool(lost),
        'native_kicad_drc_performed':False,
        'manufacturing_approved':False}
(root/'Docs'/'independent_connectivity.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert not lost, f'MISSING ELECTRICAL CONNECTIONS: {lost}'
