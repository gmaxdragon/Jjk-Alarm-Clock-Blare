#!/usr/bin/env python3
"""GGK / JJK BLARE keyboard-board prototype generator.

Produces *native editable KiCad board + schematic* with geometric routing.
KiCad CLI/DRC are separately REQUIRED before this can be manufactured.

BLARE kit: XIAO ESP32-C3, 6 MX-style switches, 6 1N4148 diodes,
3.3V passive-piezo, eight-pin 2.25-inch TFT header, 4 M3 mounts.
All no-extra-parts. 2x3 active-low diode key matrix.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from dataclasses import dataclass
from pathlib import Path
import datetime, heapq, json, math, random, uuid, itertools
import numpy as np
from shapely.geometry import Polygon, Point, LineString

ROOT = Path(__file__).resolve().parent
BOARD = ROOT / 'PCB' / 'jjkspeakerpcb.kicad_pcb'
SCHEM = ROOT / 'PCB' / 'jjkspeakerpcb.kicad_sch'
PROJECT = ROOT / 'PCB' / 'jjkspeakerpcb.kicad_pro'
random.seed(20261025)

_u_counter = itertools.count(1)
def uid():
    # Stable, unique UUIDs with a common prefix; make diffs and archives small.
    return f"a11a0000-cc00-4a11-8a11-{next(_u_counter):012x}"
def fmt(x): return f'{x:.4f}'.rstrip('0').rstrip('.') if not math.isclose(x,0) else '0'
def xy(v): return ' '.join(map(fmt, v))
def quote(s): return json.dumps(str(s), ensure_ascii=False)

NAMES = ['GND','3V3','DISP_SCK','DISP_MOSI','DISP_DC','DISP_CS',
         'PIEZO','ROW_LEFT','ROW_RIGHT','COL_TOP','COL_MIDDLE','COL_BOTTOM',
         'K1','K2','K3','K4','K5','K6']
NETIDS = {x:i+1 for i,x in enumerate(NAMES)}

def pad(layer, num, net, dx, dy, *, size=1.9, drill=0.9, shape='circle', role='thru_hole', angle=0):
    return dict(layer=layer,number=str(num),net=net,x=float(dx),y=float(dy),size=size,drill=drill,shape=shape,role=role,angle=angle)

parts=[]
def add(ref,lib,x,y,face,pads,draw='',value='',attr='through_hole'):
    symid=uid()
    part=dict(ref=ref,lib=lib,x=float(x),y=float(y),face=face,pads=pads,draw=draw,value=value or lib,symid=symid,attr=attr)
    parts.append(part)
    return part

# Compact functional T-shaped PCB, no art wings. All extents fit under 100mm.
# Display fits INSIDE the central 39mm-wide stalk, with the six-switch bar at
# the bottom. A representative TFT module is 21.08 x 73.15mm, but the exact
# kit display footprint MUST be checked before ordering.
OUTLINE=[
 (31.0,0.35),(69.0,0.35),(69.0,73.0),(71.1,75.2),
 (98.1,75.2),(99.65,76.75),(99.65,98.0),(98.0,99.65),
 (2.0,99.65),(0.35,98.0),(0.35,76.75),(1.9,75.2),
 (28.9,75.2),(31.0,73.0),
]
POLY = Polygon(OUTLINE)
assert POLY.is_valid and POLY.area > 4500

# Six switches in a single horizontal physical row. Tight 15.9mm pitch;
# stock DSA 1u keycaps (~18mm) WILL OVERLAP and cannot be installed together.
# This revision depends on 3D-printed <=15.4mm GGK narrow keycaps; verify
# actual switch top-housing dimensions and keycap skirt before fabrication.
# Electrical configuration remains 2 rows x 3 columns with 1N4148 per key.
BUTTONS = [
 ('SW1','UP',10.25,89.5, 'COL_TOP','ROW_LEFT','K1','D1'),
 ('SW2','DOWN',26.15,89.5,'COL_TOP','ROW_RIGHT','K2','D2'),
 ('SW3','TIME SET',42.05,89.5,'COL_MIDDLE','ROW_LEFT','K3','D3'),
 ('SW4','CLOCK SET',57.95,89.5,'COL_MIDDLE','ROW_RIGHT','K4','D4'),
 ('SW5','SNOOZE',73.85,89.5,'COL_BOTTOM','ROW_LEFT','K5','D5'),
 ('SW6','ALARM ON',89.75,89.5,'COL_BOTTOM','ROW_RIGHT','K6','D6'),
]

# MX PCB-mounted switch matching Cherry-MX electrical & guide-pin geometry.
# local origin is offset from nominal key center by (+2.54,-5.08).
for ref,label,cx,cy,col,row,kn,dref in BUTTONS:
    swpads=[pad('both','1',col,0,0,size=2.2,drill=1.5),
            pad('both','2',kn,-6.35,2.54,size=2.2,drill=1.5),
            pad('none','',None,-2.54,5.08,size=4.0,drill=4.0,role='np_thru_hole'),
            pad('none','',None,-7.62,5.08,size=1.7,drill=1.7,role='np_thru_hole'),
            pad('none','',None,2.54,5.08,size=1.7,drill=1.7,role='np_thru_hole')]
    add(ref,'MX_1U_PCB',cx+2.54,cy-5.08,'F',swpads,value=label)
    # Active-low scan: ROWS are pulled up, one COLUMN at a time pulled LOW.
    # Through-hole diodes: pin 1 bar/cathode -> individual switch node;
    # pin 2 anode -> row. Current flows row -> diode -> pressed switch ->
    # low column. This orientation avoids the formerly inverted matrix.
    # D9/BOOT GPIO9 is now used only as a pullup row INPUT; attached switches
    # cannot force a boot strap state until firmware actively scans columns.
    dx1=[11.25,24.5,37.75,51.0,64.25,77.5][int(ref[2:])-1]
    dx2=dx1-7.62   # B-side footprint flip places pad2 at dx1+7.62
    dy=78.1
    dpads=[pad('both','1',kn,0,0,size=1.8,drill=0.85),
           pad('both','2',row,dx2-dx1,0,size=1.8,drill=0.85)]
    add(dref,'D_DO35_P7.62',dx1,dy,'B',dpads,value='1N4148')

# XIAO real Seeed castellated-pad coordinates (from Seeed official KiCad footprint).
# Mount on BACK so the custom MX keys remain accessible from the FRONT.
# GPIO9 (D9, boot strap) and GPIO8 (D8, strap) are never driven while
# starting: the matrix ROWS are both INPUT_PULLUP. All SPI and buzzer lines
# use ordinary non-strapping GPIO. This prevents the TFT from controlling the
# BOOT strap at reset. D0 GPIO2 is deliberately unconnected.
XIAO={
 1:'',2:'DISP_DC',3:'DISP_CS',4:'COL_TOP',5:'COL_MIDDLE',6:'COL_BOTTOM',
 7:'DISP_SCK',8:'DISP_MOSI',9:'ROW_LEFT',10:'ROW_RIGHT',11:'PIEZO',
 12:'3V3',13:'GND',14:'',
}
upads=[]
for i in range(1,15):
    if i<=7:
        px,py = 0.835, -18.12+(i-1)*2.54
    else:
        px,py = 17, -2.88-(i-8)*2.54
    upads.append(pad('B',str(i),XIAO[i],-px,py,role='smd',shape='roundrect',size=(2.75,2.0),drill=0))
# Official Seeed XIAO-ESP32-C3-SMD underside lands, pads 15..22.
# The side pins already provide signals; redundant center lands are left
# isolated on *this carrier* instead of trying to route duplicate pins.
# Each NC pad still has real copper and is a protected router obstacle.
underside = [
 (15,7.62,-19.132,1.7,1.7,None),  # D3/MTDI duplicate
 (16,10.16,-19.132,1.7,1.7,None), # D5/MTDO duplicate
 (17,7.62,-16.592,1.7,1.7,None),  # EN
 (18,10.16,-16.592,1.7,1.7,None), # GND: isolated mechanically, ground by module
 (19,7.62,-14.052,1.7,1.7,None),  # D2/MTMS duplicate
 (20,10.16,-14.052,1.7,1.7,None), # D4/MTCK duplicate
 (21,4.445,-10.882,2.5,1.1,None), # VBAT, DO NOT CONNECT
 (22,4.445,-12.787,2.5,1.1,None), # GND (internal module)
]
for number,px,py,w,h,net in underside:
    upads.append(pad('B',str(number),net,-px,py,role='smd',shape='roundrect',size=(w,h),drill=0))
# Mount XIAO on PCB back under the front-facing portrait screen. Its native
# USB-C connector points UP, with the shell accessible at the top of the case.
add('U1','Seeed_XIAO_ESP32C3_Castellated',58.9,23.0,'B',upads,value='XIAO ESP32-C3',attr='smd')

# Eight-pin TFT breakout header, horizontal at TOP. Actual female-female jumper cable
# connects separate vertical screen to this header, following BLARE's kit guide.
DISPLAY={1:'GND',2:'3V3',3:'DISP_SCK',4:'DISP_MOSI',5:'3V3',
         6:'DISP_DC',7:'DISP_CS',8:'GND'}
jpads=[pad('both',str(i),DISPLAY[i],(i-1)*2.54,0,shape='rect' if i==1 else 'circle',size=1.75,drill=1.0)
       for i in range(1,9)]
add('J1','PinHeader_1x08_2.54',41.11,67,'B',jpads,value='TFT 8PIN')

# No assumption that an active magnetic buzzer is safe on GPIO. The board is
# wired directly for the advertised LOW CURRENT 3.3V PIEZO only; kit part must
# be verified before assembly. Mounted BACK, vent faces case opening.
add('BZ1','Piezo_P12_P7.62',46.19,46,'B',[
    pad('both','1','PIEZO',0,0,shape='rect',size=1.9,drill=0.9),
    pad('both','2','GND',7.62,0,size=1.9,drill=0.9)],value='3.3V PIEZO')

# Hole centers chosen outside MX PCB guide holes and typical 1u keycaps.
HOLES=[('H1',35.6,38),('H2',64.4,38)]
for ref,hx,hy in HOLES:
    add(ref,'MountingHole_3.2',hx,hy,'F',[
        pad('none','',None,0,0,size=3.2,drill=3.2,role='np_thru_hole')],value='M3',attr='board_only exclude_from_pos_files exclude_from_bom')

# Calculate pad locations. Backside pads keep local X/Y as seen in the KiCad
# B-side footprint coordinate system, allowing pcbnew to perform mirroring.
# IMPORTANT: This generator stores B-side footprint x-values as back-view
# coordinates; in board drawing, pcbnew flips local x -> -x. Physical target:
# place front-view module left pad column at x39.935; right at x56.10.
def target(p, q):
    # On bottom layer, local x mirrors; anchor at x56.935 so pad1 physical x56.1,
    # and pad8 physical x39.935. PCB KiCad F-frame coordinates derived by flip.
    x=p['x'] + q['x']
    y=p['y'] + q['y']
    return (round(x,4),round(y,4))

# Board back-side footprints anchor x-values reversed from front-view:
# We want XIAO center x48.0 and the USB near board bottom.
for p in parts:
    if p['ref']=='U1':
        p['x']=58.9      # Canonical KiCad B-side physical flip; body x41.1..58.9
    if p['ref']=='J1':
        p['x']=41.11     # KiCad back footprint pins x41.11..58.89
    if p['ref']=='BZ1':
        p['x']=46.19     # KiCad back footprint piezo center x50.0

PADS=[]
for p in parts:
    for q in p['pads']:
        point=target(p,q)
        o=dict(part=p['ref'],**q,at=point)
        PADS.append(o)
assert all(POLY.buffer(-1.05).contains(Point(q['at'])) for q in PADS if q['role']!='np_thru_hole'), [(q['part'],q['number'],q['at']) for q in PADS if q['role']!='np_thru_hole' and not POLY.buffer(-1.05).contains(Point(q['at']))]

# 2-layer A* router, generous chip pad keepouts, clearance-aware rounded line
# segments. Internal geometric router report is NOT a substitute for KiCad DRC.
GRID=0.5
W=int(100/GRID)+1
H=int(100/GRID)+1
COST_TURN=.16
# Each pad's actual copper radius / rectangle half-size, conservatively covered
# as a circular obstacle to avoid shortage of clearance on 45-degree traces.
def copper_radius(q):
    size=q['size']
    if isinstance(size,tuple):return max(size)/2+.12
    return size/2

def ixy(at):return (int(round(at[0]/GRID)),int(round(at[1]/GRID)))
def real(node):return (node[0]*GRID,node[1]*GRID)

polyMask=np.zeros((H,W),dtype=np.bool_)
for y in range(H):
    for x in range(W):
        xx,yy=real((x,y))
        # Edge cuts copper keepout, with copper clearance from outer edge.
        polyMask[y,x]=POLY.buffer(-.68).contains(Point(xx,yy))

padBlocks=np.zeros((2,H,W),dtype=np.int16) # zero free, -1 NPTH, netID other
for q in PADS:
    px,py=q['at'];ir=copper_radius(q)
    if q['role']=='np_thru_hole': layers=(0,1); blocker=-1;extra=.65
    elif q['role']=='smd': layers=(1,);blocker=NETIDS[q['net']] if q['net'] else -1;extra=.48
    else: layers=(0,1);blocker=NETIDS.get(q['net'],0);extra=.48
    # For SMD rectangular pads use radius e.g. 1.5 + .48
    rad=ir+extra
    x0=max(0,int((px-rad)/GRID)-1);x1=min(W,int((px+rad)/GRID)+2)
    y0=max(0,int((py-rad)/GRID)-1);y1=min(H,int((py+rad)/GRID)+2)
    for yy in range(y0,y1):
        for xx in range(x0,x1):
            if (px-xx*GRID)**2+(py-yy*GRID)**2 <= rad**2:
                for z in layers:
                    if blocker == -1: padBlocks[z,yy,xx]=-1
                    elif padBlocks[z,yy,xx]==0: padBlocks[z,yy,xx]=blocker
                    elif padBlocks[z,yy,xx]!=blocker: padBlocks[z,yy,xx]=-1
# Also forbid 3mm radius around each M3 screw/hole (screw head + trace).
for q in PADS:
    if q['role']!='np_thru_hole' or not q['part'].startswith('H'):continue
    px,py=q['at'];rad=3.5
    for yy in range(max(0,int((py-rad)/GRID)-1),min(H,int((py+rad)/GRID)+2)):
        for xx in range(max(0,int((px-rad)/GRID)-1),min(W,int((px+rad)/GRID)+2)):
            if (px-xx*GRID)**2+(py-yy*GRID)**2 <= rad**2:padBlocks[:,yy,xx]=-1

trackBlocks=np.zeros((2,H,W),dtype=np.int16)
segments=[]
vias=[]

byNet=defaultdict(list)
for q in PADS:
    if q['net']:byNet[q['net']].append(q)

# Via larger than normal tracks; run a local clearance check at via placement.
def validnode(node, net, via=False):
    x,y,z=node
    if x<0 or y<0 or x>=W or y>=H:return False
    if not polyMask[y,x]:return False
    ID=NETIDS[net]
    rr=2 if via else 0
    for ly in ((0,1) if via else (z,)):
        for yy in range(y-rr,y+rr+1):
            for xx in range(x-rr,x+rr+1):
                if yy<0 or xx<0 or yy>=H or xx>=W or not polyMask[yy,xx]:return False
                b=padBlocks[ly,yy,xx]
                t=trackBlocks[ly,yy,xx]
                if b not in (0,ID) or t not in (0,ID):return False
    return True

# Diagonal movement may cut corners; require both orthogonal side cells clear.
DIRECTIONS=[(1,0,1),(0,1,1),(-1,0,1),(0,-1,1),
            (1,1,1.414),(-1,1,1.414),(1,-1,1.414),(-1,-1,1.414)]
def route_pair(net,a,b):
    st0=ixy(a['at']); en0=ixy(b['at']);
    zs=(1,) if a['role']=='smd' else (0,1)
    ze=(1,) if b['role']=='smd' else (0,1)
    starts=[(st0[0],st0[1],z) for z in zs]
    ends={(en0[0],en0[1],z) for z in ze}
    # Preserve both exact pin endpoints; allow any pad cell of own net.
    order=sorted(ends,key=lambda e: min(math.dist(e[:2],s[:2]) for s in starts))
    def heuristic(t):return min(math.hypot(t[0]-end[0],t[1]-end[1]) + (0 if t[2]==end[2] else 11) for end in order)
    prev={};cost={}; pq=[];seq=itertools.count()
    for s in starts:
        cost[s]=0;heapq.heappush(pq,(heuristic(s),next(seq),s))
    expanded=0
    maxExpand=95000
    while pq:
        _,_,node=heapq.heappop(pq)
        g=cost[node]
        expanded+=1
        if node in ends:
            path=[node]
            while node in prev:
                node=prev[node];path.append(node)
            path.reverse()
            return path,expanded
        if expanded>maxExpand:break
        x,y,z=node
        for dx,dy,d in DIRECTIONS:
            v=(x+dx,y+dy,z)
            if not validnode(v,net):continue
            if dx and dy:
                if not validnode((x+dx,y,z),net) or not validnode((x,y+dy,z),net):continue
            newg=g+d+(0.15 if z==0 else 0)
            if newg<cost.get(v,1e10):
                cost[v]=newg;prev[v]=node
                heapq.heappush(pq,(newg+heuristic(v),next(seq),v))
        # Via switch on same cell: two layers must be clear for via hole.
        v=(x,y,1-z)
        if validnode(node,net,via=True):
            newg=g+18
            if newg<cost.get(v,1e10):
                cost[v]=newg;prev[v]=node
                heapq.heappush(pq,(newg+heuristic(v),next(seq),v))
    return None,expanded

def mark(net,path):
    ID=NETIDS[net]
    # Inflate tracks by 0.5mm = width/2 + clearance(0.25) + margin(0.125)
    for (x,y,z) in path:
        for yy in range(max(0,y-1),min(H,y+2)):
            for xx in range(max(0,x-1),min(W,x+2)):
                if (xx-x)**2+(yy-y)**2<=1.25 and trackBlocks[z,yy,xx] in (0,ID):
                    trackBlocks[z,yy,xx]=ID
    for prev,cur in zip(path,path[1:]):
        if prev[2]!=cur[2]:
            vias.append((real(cur),net))
    # compress contiguous same-layer collinear path into long segments
    a=path[0];old=path[0];delta=None
    for v in path[1:]:
        d=(v[0]-old[0],v[1]-old[1],v[2]-old[2])
        if delta is not None and (d!=delta or v[2]!=a[2]):
            if a[:2]!=old[:2]:segments.append((real(a),real(old),'F.Cu' if a[2]==0 else 'B.Cu',net))
            a=old
        delta=d
        old=v
    if a[:2]!=old[:2]:segments.append((real(a),real(old),'F.Cu' if a[2]==0 else 'B.Cu',net))

# Route all electrical nets explicitly, including GND. Ground copper is not
# assumed connected merely because an unfilled zone exists. KiCad native DRC
# and final zone refill remain mandatory before any manufacturing release.
routing_report=[]
order=sorted([n for n in NAMES if n!='GND'],key=lambda n: (len(byNet[n])>3, -len(byNet[n]),n))
# prioritize chip connections to multiple switch/diode pads (higher fan-out)
# Prioritize pull-up ROW buses before the other nets; otherwise the display
# breakout traces can cut off the two D8/D9 ROW endpoints entirely.
priority=['ROW_LEFT','ROW_RIGHT', 'DISP_DC','DISP_MOSI','DISP_SCK',
          'DISP_CS','PIEZO','3V3','K6','K5','K4','K3','K2','K1',
          'COL_BOTTOM','COL_MIDDLE','COL_TOP','GND']
import os
if os.environ.get('GGK_ROUTE_PRIORITY'):
    priority=os.environ['GGK_ROUTE_PRIORITY'].split(',')
for net in priority:
    endpoints=byNet[net]
    if len(endpoints)<2:continue
    attached=[endpoints[0]]
    todo=endpoints[1:]
    while todo:
        # greedy minimum-distance next connection; fallback multiple attempts
        candidates=sorted([(math.dist(a['at'],b['at']), a,b) for a in attached for b in todo], key=lambda z:z[0])
        answer=None
        for dist,a,b in candidates[:min(len(candidates),30)]:
            result,expanded=route_pair(net,a,b)
            if result is not None:
                answer=(a,b,result,expanded);break
        if not answer:
            routing_report.append(dict(net=net,status='UNROUTED',attached=len(attached),remaining=len(todo)))
            break
        a,b,path,nodes=answer
        mark(net,path)
        attached.append(b);todo.remove(b)
        routing_report.append(dict(net=net,status='ROUTED',to=b['part']+':'+b['number'],frompad=a['part']+':'+a['number'],vias=sum(1 for u,v in zip(path,path[1:]) if u[2]!=v[2]),expanded=nodes))

# GND must now have explicit pads-to-pads routes, independent of zone fills.
# Zones still exist as supplemental copper planes and need native refill before fab.

def fp_text(layer,kind,s,x,y,size=.8):
    mirror = ' (justify mirror)' if layer.startswith('B.') else ''
    return f'(fp_text {kind} {quote(s)} (at {fmt(x)} {fmt(y)}) (layer {quote(layer)}) (effects (font (size {fmt(size)} {fmt(size)}) (thickness .13)){mirror}))'

def fp_line(x1,y1,x2,y2,layer='F.SilkS',width=.12):
    return f'(fp_line (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) (stroke (width {fmt(width)}) (type solid)) (layer {quote(layer)}) (uuid {quote(uid())}))'

def fp_rect(x1,y1,x2,y2,layer='F.SilkS',width=.12):
    return f'(fp_rect (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) (stroke (width {fmt(width)}) (type solid)) (fill none) (layer {quote(layer)}) (uuid {quote(uid())}))'

def footprint(p):
    layer='B.Cu' if p['face']=='B' else 'F.Cu'; base=layer[:1]; sig=[]
    sig.append(f'(footprint {quote("GGK:"+p["lib"])} (layer {quote(layer)}) (uuid {quote(uid())}) (at {fmt(p["x"])} {fmt(p["y"])}) (attr {p["attr"]})')
    refat=(0,-10.8) if p['ref'].startswith('SW') else (0,-3)
    if p['ref']=='U1': refat=(-8.9,-23.5)
    if p['ref'].startswith('H'): refat=(0,4)
    sig.append(fp_text(base+'.Fab','reference',p['ref'],*refat,size=.8))
    sig.append(fp_text(base+'.Fab','value',p['value'],0,12 if p['lib'].startswith('MX') else 4,size=.7))
    sig.append(f'(path "/{p["symid"]}")')
    if p['lib'].startswith('MX'):
        # Courtyard represents the verified SWITCH HOUSING ONLY at tight pitch,
        # not a 19.05mm full-size keycap. Narrow printed keycaps needed.
        sig.extend([fp_rect(-9.525,-1.905,4.445,12.065,layer='F.Fab'),
                    fp_rect(-10.44,-2.82,5.36,12.98,layer='F.CrtYd',width=.05)])
    elif p['ref']=='U1':
        # The XIAO's real component envelope is in the Tinkercad mechanical
        # guide, not duplicated as ad-hoc reversed footprint graphics here.
        # Only the canonical Seeed pad geometry participates in DRC.
        pass
    elif p['ref']=='J1':sig.append(fp_rect(-1.45,-1.45,19.23,1.45,'B.SilkS',.1))
    elif p['ref']=='BZ1':
        sig.append(f'(fp_circle (center 3.81 0) (end 9.81 0) (stroke (width .12) (type solid)) (fill none) (layer "B.SilkS") (uuid {quote(uid())}))')
        sig.append(fp_text('B.Fab','user','+',-1,3.5,size=.85))
    elif p['ref'].startswith('D'):
        sig.append(fp_rect(-2.1,-1.0,2.1,1.0,base+'.Fab',.12))
        sig.append(fp_line(-1.2,-1.5,-1.2,1.5,base+'.Fab',.3)) # cathode stripe pad1
    elif p['ref'].startswith('H'):
        pass
    for q in p['pads']:
        if q['role']=='np_thru_hole':
            sig.append(f'(pad "" np_thru_hole circle (at {xy((q["x"],q["y"]))}) (size {fmt(q["size"])} {fmt(q["size"])}) (drill {fmt(q["drill"])}) (layers "*.Cu" "*.Mask") (uuid {quote(uid())}))')
            continue
        if q['role']=='smd':layers='"B.Cu" "B.Paste" "B.Mask"';smdshape='roundrect';dr=''
        else:layers='"*.Cu" "*.Mask"';smdshape=q['shape'] if q['shape']!='roundrect' else 'rect';dr=f'(drill {fmt(q["drill"])})'
        siz=q['size']
        if isinstance(siz,tuple):w,h=siz
        else:w=h=siz
        shape=smdshape if q['role']=='smd' else q['shape']
        special='(roundrect_rratio .2)' if q['role']=='smd' else ''
        net=f'(net {NETIDS[q["net"]]} {quote(chr(47)+q["net"])})' if q['net'] else ''
        sig.append(f'(pad {quote(q["number"])} {q["role"]} {shape} (at {xy((q["x"],q["y"]))}) (size {fmt(w)} {fmt(h)}) {dr} (layers {layers}) {special} {net} (uuid {quote(uid())}))')
    sig.append(')')
    return '\n'.join(sig)

# No decorative images, branding graphics, or key labels on manufactured silkscreen.
# The screen body appears ONLY as a mechanical reference on Dwgs.User.
# Avoid claiming special colors are in PCB data; solder-mask finish chosen at fab.
def gtext(s,x,y,size=1.25,thickness=.19,layer='F.SilkS',angle=0):
    mirror = ' (justify mirror)' if layer.startswith('B.') else ''
    return f'(gr_text {quote(s)} (at {fmt(x)} {fmt(y)} {angle}) (layer {quote(layer)}) (effects (font (size {fmt(size)} {fmt(size)}) (thickness {fmt(thickness)}) (bold yes)){mirror}) (uuid {quote(uid())}))'

def gline(x1,y1,x2,y2,width=.25,layer='F.SilkS'):
    return f'(gr_line (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) (stroke (width {fmt(width)}) (type solid)) (layer {quote(layer)}) (uuid {quote(uid())}))'

PCB_HEADER='''(kicad_pcb
 (version 20221018)
 (generator "pcbnew")
 (general (thickness 1.6))
 (paper "A4")
 (layers
  (0 "F.Cu" signal)
  (31 "B.Cu" signal)
  (32 "B.Adhes" user)
  (33 "F.Adhes" user)
  (34 "B.Paste" user)
  (35 "F.Paste" user)
  (36 "B.SilkS" user)
  (37 "F.SilkS" user)
  (38 "B.Mask" user)
  (39 "F.Mask" user)
  (40 "Dwgs.User" user)
  (41 "Cmts.User" user)
  (42 "Eco1.User" user)
  (43 "Eco2.User" user)
  (44 "Edge.Cuts" user)
  (45 "Margin" user)
  (46 "B.CrtYd" user)
  (47 "F.CrtYd" user)
  (48 "B.Fab" user)
  (49 "F.Fab" user)
 )
 (setup (pad_to_mask_clearance 0) (solder_mask_min_width 0.05))
 (net 0 "")
'''
board_text=[PCB_HEADER]
for n in NAMES:board_text.append(f'(net {NETIDS[n]} {quote(chr(47)+n)})')
for p in parts:board_text.append(footprint(p))
for a,b,layer,net in segments:
    board_text.append(f'(segment (start {xy(a)}) (end {xy(b)}) (width 0.25) (layer {quote(layer)}) (net {NETIDS[net]}) (uuid {quote(uid())}))')
for at,net in vias:
    board_text.append(f'(via (at {xy(at)}) (size 0.7) (drill 0.35) (layers "F.Cu" "B.Cu") (net {NETIDS[net]}) (uuid {quote(uid())}))')
for a,b in zip(OUTLINE,OUTLINE[1:]+OUTLINE[:1]):
    board_text.append(gline(*a,*b,.05,'Edge.Cuts'))
# MINIMAL PCB: a T-shaped board with only necessary electrical parts.
# Intentionally no F.SilkS key names or decorative images. Screen is 21.08 x
# 73.15mm (example module body) centered on front, within the central stalk.
# The exact kit screen must be measured before the case is final.
board_text.append(gtext('GGK ALARM REV D',50,54,.8,.12,layer='B.Fab'))
board_text.append(gtext('6 KEY MATRIX / PORTRAIT TFT',50,60,.8,.1,layer='B.Fab'))
for rect in (((39.46,1.15),(60.54,74.3)),):
    (x1,y1),(x2,y2)=rect
    for (a,b),(c,d) in zip([(x1,y1),(x2,y1),(x2,y2),(x1,y2)],[(x2,y1),(x2,y2),(x1,y2),(x1,y1)]):
        board_text.append(gline(a,b,c,d,.12,'Dwgs.User'))
board_text.append(gtext('PORTRAIT TFT REF ONLY 21.08 X 73.15 MM',50,70,.55,.09,layer='Dwgs.User'))
# copper ground fills initially unfilled (KiCad GUI or CI fills using pcbnew)
zone_pts=' '.join(f'(xy {xy(v)})' for v in OUTLINE)
for layer in ('F.Cu','B.Cu'):
    board_text.append(f'''(zone (net {NETIDS['GND']}) (net_name "/GND") (layer "{layer}")
        (uuid "{uid()}") (hatch edge 0.508) (connect_pads (clearance 0.45))
        (min_thickness 0.25) (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
        (polygon (pts {zone_pts})))''')
board_text.append(')')
BOARD.write_text('\n'.join(board_text),encoding='utf-8')

# Self-contained schematic: embedded symbols and global per-net labels.
# Two M3 mounting holes: lower bar supported by printed case channels.
SCH_HEADER=f'''(kicad_sch (version 20231120) (generator "eeschema")
(uuid {quote(uid())}) (paper "A4")
'''
def effects(size=1.27,align=''):
    return f'(effects (font (size {fmt(size)} {fmt(size)}) (thickness .12)) {align})'

def schem_pin(num,name,xx,yy,rot,kind='passive'):
    return f'''(pin {kind} line (at {fmt(xx)} {fmt(yy)} {rot}) (length 2.54)
      (name {quote(name)} {effects(.95)}) (number {quote(num)} {effects(.95)}))'''

def lib_symbol(name,pin_defs,rect,circle=False,reference='U',descr=''):
    x1,y1,x2,y2=rect
    pr=f'(property "Reference" {quote(reference)} (at 0 {fmt(max(y1,y2)+3)} 0) {effects()})'
    pv=f'(property "Value" {quote(name)} (at 0 {fmt(min(y1,y2)-3)} 0) {effects(.9)})'
    shape=(f'(circle (center 0 0) (radius 5.08) (stroke (width .25) (type default)) (fill (type none)))'
           if circle else f'(rectangle (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) (stroke (width .25) (type default)) (fill (type none)))')
    return f'''(symbol "GGK:{name}" (pin_names (offset .9)) (in_bom yes) (on_board yes)
      {pr} {pv} (symbol {quote(name+'_0_1')} {shape})
      (symbol {quote(name+'_1_1')} {' '.join(schem_pin(*pin) for pin in pin_defs)}))'''

xpin=[]
for i in range(1,8):xpin.append((str(i),f'D{i-1}',-21.59,15.24-(i-1)*5.08,0))
for i,name in zip(range(8,15),['D7','D8','D9','D10','3V3','GND','VBUS']):
    xpin.append((str(i),name,21.59,15.24-(i-8)*5.08,180))
for i,name in zip(range(15,23),['D3_DUP','D5_DUP','EN','GND2','D2_DUP','D4_DUP','VBAT','GND3']):
    xpin.append((str(i),name,-15.24+(i-15)*5.08,22.86,270))
# Keep the unused 8 underside lands isolated; the other side pads perform I/O.
SWPINS=[('1','C',-7.62,0,0),('2','A',7.62,0,180)]
DPINS=[('1','K',-7.62,0,0),('2','A',7.62,0,180)]
JPINS=[(str(i),str(i),-10.16,10.16-2.54*(i-1),0) for i in range(1,9)]
BPINS=[('1','+',-7.62,0,0),('2','-',7.62,0,180)]
lib=[lib_symbol('XIAO_ESP32_C3',xpin,(-17.78,20.32,17.78,-20.32)),
     lib_symbol('MX_1U_PCB',SWPINS,(-5.08,2.54,5.08,-2.54),reference='SW'),
     lib_symbol('D_DO35_P7.62',DPINS,(-5.08,2.54,5.08,-2.54),reference='D'),
     lib_symbol('HEADER_TFT_1x08',JPINS,(-7.62,12.7,7.62,-10.16),reference='J'),
     lib_symbol('PIEZO_PASSIVE',BPINS,(-5.08,5.08,5.08,-5.08),circle=True,reference='BZ'),
     lib_symbol('M3_MOUNT',[],(-2.54,2.54,2.54,-2.54),reference='H')]
S=['(lib_symbols '+ '\n'.join(lib)+')']
# all signals are labeled on short pin stubs; our schematic provides the same
# declared KiCad netlist as board-file pads, by reference pin-number.
SCH_REF_NET={}
for p in parts:
    d={}
    for q in p['pads']:
        if q['number']:d[q['number']]=q['net']
    SCH_REF_NET[p['ref']]=d

# Pin symbol locations for each part type (in local schematic coordinates)
positions={'XIAO_ESP32_C3':xpin,'MX_1U_PCB':SWPINS,'D_DO35_P7.62':DPINS,
           'HEADER_TFT_1x08':JPINS,'PIEZO_PASSIVE':BPINS,'M3_MOUNT':[]}
placements={'U1':(81.28,81.28,'XIAO_ESP32_C3'),
            'J1':(81.28,161.29,'HEADER_TFT_1x08'),
            'BZ1':(144.78,161.29,'PIEZO_PASSIVE')}
for idx,(swref,_,*_) in enumerate(BUTTONS):
    placements[swref]=(144.78,44.45+idx*17.78,'MX_1U_PCB')
    placements[f'D{idx+1}']=(190.5,44.45+idx*17.78,'D_DO35_P7.62')
for i,(ref,_,_) in enumerate(HOLES):placements[ref]=(228.6,144.78+12.7*i,'M3_MOUNT')

for part in parts:
    ref=part['ref'];x,y,typ=placements[ref];pin_def=positions[typ]
    # lib symbol x positive right, y positive up; instance y positive down.
    body=f'''(symbol (lib_id {quote('GGK:'+typ)}) (at {fmt(x)} {fmt(y)} 0) (unit 1)
       (in_bom {'no' if ref.startswith('H') else 'yes'}) (on_board yes) (dnp no) (uuid {quote(part['symid'])})
       (property "Reference" {quote(ref)} (at {fmt(x)} {fmt(y-25 if ref=='U1' else y-7.3)} 0) {effects(1)})
       (property "Value" {quote(part['value'])} (at {fmt(x)} {fmt(y+25 if ref=='U1' else y+7.3)} 0) {effects(.9)})
       (property "Footprint" {quote('GGK:'+part['lib'])} (at {fmt(x)} {fmt(y+10)} 0) {effects(.8,'(hide yes)')})
       {' '.join(f'(pin {quote(pd[0])} (uuid {quote(uid())}))' for pd in pin_def)}
       (instances (project "jjkspeakerpcb" (path "/" (reference {quote(ref)}) (unit 1)))))'''
    S.append(body)
    for num,pname,dx,dy,rot in pin_def:
        px,py=x+dx,y-dy
        net=SCH_REF_NET[ref].get(num)
        if not net:
            S.append(f'(no_connect (at {fmt(px)} {fmt(py)}) (uuid {quote(uid())}))')
            continue
        if rot==270:
            ex,ey=px,py-5.08
        else:
            direction=-1 if rot==0 else 1
            ex,ey=px+direction*5.08,py
        S.append(f'(wire (pts (xy {fmt(px)} {fmt(py)}) (xy {fmt(ex)} {fmt(ey)})) (stroke (width 0) (type default)) (uuid {quote(uid())}))')
        S.append(f'(label {quote(net)} (at {fmt(ex)} {fmt(ey)} 0) {effects(.9)} (uuid {quote(uid())}))')

# Descriptive fields; no copyrighted illustrations.
S.append(f'''(text "GGK ALARM / BLARE - SIX-KEY SINGLE ROW PCB (AUDIT Rev D)"
   (at 44 21 0) {effects(1.4)} (uuid {quote(uid())}))''')
S.append(f'''(text "1N4148 cathode stripes on SWITCH K1..K6; anodes on ROW; active-low 2x3 matrix."
   (at 48 27 0) {effects(1)} (uuid {quote(uid())}))''')
S.append(f'''(text "Power via XIAO USB-C only; battery pack output must stay ON for alarm."
   (at 48 33 0) {effects(1)} (uuid {quote(uid())}))''')
S.append(f'''(text "TFT 8-pin: 1 GND,2 3V3,3 SCK,4 MOSI,5 RST=3V3,6 DC,7 CS,8 BL=GND."
   (at 48 35.8 0) {effects(.8)} (uuid {quote(uid())}))''')
S.append(f'''(text "Buzzer: 3.3V LOW-CURRENT PASSIVE PIEZO only; verify exact kit part before soldering."
   (at 48 39 0) {effects(.8)} (uuid {quote(uid())}))''')
S.append('(embedded_fonts no) )')
SCHEM.write_text(SCH_HEADER+'\n'.join(S),encoding='utf-8')
PROJECT.write_text(json.dumps({'meta':{'version':1}},indent=2)+'\n')

report={
 'design':'GGK ALARM Rev C / T-SHAPE / NO ART / USB ONLY', 'board_outline_mm':[99.3,99.3],
 'area_mm2':round(POLY.area,2),'switches':6,'mx_matrix':'2 rows x 3 cols',
 'diodes':6,'tft':'ST7789 76x284 (portrait display, 8-pin cable header)',
 'key_pitch_mm':15.9, 'stock_DSA_keycaps_fit':False, 'narrow_3d_printed_keycaps_required':True,
 'parts':{p['ref']:dict(value=p['value'],side=p['face'],xy=(p['x'],p['y'])) for p in parts},
 'nets':{net:[q['part']+':'+q['number'] for q in pads] for net,pads in byNet.items()},
 'routing':routing_report, 'trace_segments':len(segments),'vias':len(vias),
 'unrouted':len([r for r in routing_report if r['status']=='UNROUTED']),
 'verification':'UNVERIFIED BY KICAD CLI; board is design prototype until ERC/DRC and net connectivity validate'
}
(ROOT/'Docs'/'generator_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['area_mm2','switches','diodes','trace_segments','vias','unrouted']},indent=2))
print('Wrote',BOARD,BOARD.stat().st_size,'bytes')
print('Wrote',SCHEM,SCHEM.stat().st_size,'bytes')
