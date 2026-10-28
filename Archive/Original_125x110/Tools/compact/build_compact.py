#!/usr/bin/env python3
"""Preserve original native parts and net assignments; reroute 95 mm compact PCB.
Requires numpy. Native KiCad ERC/DRC is a separate release gate.
"""
from pathlib import Path
from collections import defaultdict
import copy,heapq,itertools,json,math,os,re,sys,time,uuid
import numpy as np
from sexpr import loads,dumps,Q,child,children,get
ROOT=Path(os.environ.get('JJK_ROOT',Path(__file__).resolve().parents[2]))
SOURCE=ROOT/'PCB/jjkspeakerpcb.kicad_pcb'
OUT=ROOT/'Revisions/Compact_95/PCB';OUT.mkdir(parents=True,exist_ok=True)
SIZE=95.0;GRID=.25;N=int(SIZE/GRID)+1
board=loads(SOURCE.read_text())
U=lambda:Q(str(uuid.uuid4()))
P={'J1':(12.,10.,0),'J2':(27.24,10.,0),'J3':(43.,12.,90),
'C1':(44.,21.,0),'C2':(55.,21.,0),'R1':(15.,35.,0),
'BZ1':(77.2,15.,0),'Q1':(78.,31.,0),'R2':(62.,29.,0),'R3':(62.,37.,0),'D7':(77.,39.,0),
'H1':(5.,5.,0),'H2':(90.,5.,0),'H3':(5.,90.,0),'H4':(90.,90.,0)}
centers={};labels={'SW1':'UP','SW2':'DOWN','SW3':'TIME SET','SW4':'CLOCK SET','SW5':'SNOOZE','SW6':'ALARM ON'}
for c,x in enumerate([28.45,47.5,66.55]):
 for row,y in enumerate([60.,82.]):
  i=c*2+row+1;ref=f'SW{i}';centers[ref]=[x,y]
  P[ref]=(x+2.54,y-5.08,0);P[f'D{i}']=(x-3.81,47.0 if row==0 else 70.0,0)
# Keep inherited geometry, matching symbol UUIDs and exact pad/net mapping.
oldmap={};pads=[];fps=[]
for f0 in children(board,'footprint'):
 f=copy.deepcopy(f0);ref=next(p[2] for p in children(f,'property') if p[1]=='Reference')
 a=child(f,'at');oldrot=float(a[3]) if len(a)>3 else 0
 px,py,rot=P[str(ref)];a[:]=['at',str(px),str(py),str(rot)]
 f[:]=[v for v in f if not(isinstance(v,list) and v and v[0]=='locked')]
 for prop in children(f,'property'):
  ef=child(prop,'effects')
  if prop[1]=='Reference':
   # Use a readable reference above every body; no misleading footprint values.
   if str(ref).startswith('SW'):child(prop,'at')[:]=['at','-2.54','-4','0']
   elif ref=='BZ1':child(prop,'at')[:]=['at','3.8','-7.5','0']
   else:
    at=child(prop,'at')
    if at and len(at)>3:at[3]='0'
   font=child(ef,'font');child(font,'size')[1:]=['0.8','0.8'];child(font,'thickness')[1:]=['0.12']
  else:
   if ef is not None and child(ef,'hide') is None:ef.append(['hide','yes'])
 for p in children(f,'pad'):
  la=child(p,'at');dx,dy=map(float,la[1:3]);th=math.radians(rot)
  x=px+dx*math.cos(th)+dy*math.sin(th);y=py-dx*math.sin(th)+dy*math.cos(th)
  if len(la)>3:la[3]=str(float(la[3])-oldrot+rot)
  sz=list(map(float,child(p,'size')[1:3]));net=str(get(p,'net',''))
  typ=str(p[2]);shape=str(p[3]);width,height=sz
  angle=math.radians(float(la[3]) if len(la)>3 else rot)
  # Pads are all THT. Preserve exact shape; rotate rectangular bounds.
  if round(math.degrees(angle))%180==90:width,height=height,width
  drill=child(p,'drill');d=float(drill[1]) if drill and drill[1]!='oval' else 0
  pads.append({'ref':str(ref),'num':str(p[1]),'x':x,'y':y,'w':width,'h':height,'net':net,'shape':shape,'type':typ,'drill':d})
 oldmap[str(ref)]={str(p[1]):str(get(p,'net','')) for p in children(f0,'pad') if p[1]}
 fps.append(f)
netnames=sorted(set(p['net'] for p in pads if p['net']))
netids={n:i+1 for i,n in enumerate(netnames)}
by=defaultdict(list)
for p in pads:
 if p['net'] and not p['net'].startswith('unconnected-'):by[p['net']].append(p)
# Conservative routing lattice: foreign copper/hole inflation includes the
# largest new half-track width, 0.2mm clearance and a rasterization margin.
blocks=np.zeros((N,N),dtype=np.uint64)
for p in pads:
 x,y,w,h=p['x'],p['y'],p['w'],p['h'];extra=.50
 if p['type']=='np_thru_hole':bit=np.uint64(1)<<np.uint64(63);extra=.60
 else:bit=np.uint64(1)<<np.uint64(netids[p['net']])
 if p['ref'].startswith('H'):w=h=7.8;extra=.25
 x0=max(0,int((x-w/2-extra)/GRID)-1);x1=min(N,int((x+w/2+extra)/GRID)+2)
 y0=max(0,int((y-h/2-extra)/GRID)-1);y1=min(N,int((y+h/2+extra)/GRID)+2)
 yy,xx=np.mgrid[y0:y1,x0:x1];rx=abs(xx*GRID-x);ry=abs(yy*GRID-y)
 if p['shape']=='circle' or p['type']=='np_thru_hole':inside=(rx*rx+ry*ry)<=(w/2+extra)**2
 elif p['shape']=='oval':
  # Capsule using exact axis lengths.
  if w<h:inside=rx**2+np.maximum(ry-(h-w)/2,0)**2<=(w/2+extra)**2
  else:inside=ry**2+np.maximum(rx-(w-h)/2,0)**2<=(h/2+extra)**2
 else:inside=(np.maximum(rx-w/2,0)**2+np.maximum(ry-h/2,0)**2)<=extra**2
 blocks[y0:y1,x0:x1][inside]|=bit
blocks[:4,:]=np.uint64(1)<<np.uint64(63);blocks[-4:,:]=np.uint64(1)<<np.uint64(63)
blocks[:,:4]=np.uint64(1)<<np.uint64(63);blocks[:,-4:]=np.uint64(1)<<np.uint64(63)
tracks=np.zeros((2,N,N),np.uint64)
segments=[];vias=[];report=[]
DIR=[(1,0,1.),(0,1,1.),(-1,0,1.),(0,-1,1.),(1,1,2**.5),(-1,1,2**.5),(1,-1,2**.5),(-1,-1,2**.5)]
xy=lambda p:(int(round(p['x']/GRID)),int(round(p['y']/GRID)))
def route(net,a,b):
 bit=np.uint64(1)<<np.uint64(netids[net]);mask=np.uint64(~bit)
 pblocked=(blocks&mask)!=0
 banned=np.logical_or(pblocked[None,:,:],(tracks&mask)!=0)
 sx,sy=xy(a);tx,ty=xy(b)
 starts=[(sx,sy,0),(sx,sy,1)];ends={(tx,ty,0),(tx,ty,1)}
 if any(banned[z,sy,sx] for z in (0,1)) or any(banned[z,ty,tx] for z in (0,1)):
  return None,0
 h=lambda x,y: max(abs(x-tx),abs(y-ty))+.41421356237*min(abs(x-tx),abs(y-ty))
 pq=[];cost={};prev={};seq=itertools.count()
 for n in starts:cost[n]=0;heapq.heappush(pq,(h(sx,sy),next(seq),0,n))
 expanded=0
 while pq:
  _,_,g,n=heapq.heappop(pq)
  if g>cost[n]+1e-8:continue
  if n in ends:
   path=[n]
   while n in prev:n=prev[n];path.append(n)
   return path[::-1],expanded
  expanded+=1
  if expanded>500000:break
  x,y,z=n
  for dx,dy,d in DIR:
   X,Y=x+dx,y+dy
   if X<0 or X>=N or Y<0 or Y>=N or banned[z,Y,X]:continue
   if dx and dy and (banned[z,y,X] or banned[z,Y,x]):continue
   v=X,Y,z
   # Layer preference helps avoid congested single-layer meanders.
   extra=.04 if (z==0 and dy and not dx) or (z==1 and dx and not dy) else 0
   ng=g+d+extra
   if ng+1e-8<cost.get(v,1e30):
    cost[v]=ng;prev[v]=n;heapq.heappush(pq,(ng+h(X,Y),next(seq),ng,v))
  if 4<x<N-5 and 4<y<N-5 and not banned[:,y-3:y+4,x-3:x+4].any():
   v=x,y,1-z;ng=g+32
   if ng<cost.get(v,1e30):cost[v]=ng;prev[v]=n;heapq.heappush(pq,(ng+h(x,y),next(seq),ng,v))
 return None,expanded

def width(n):return .5 if n in ['+3V3','GND','/NEG'] else .25

def mark(net,path,a,b):
 bit=np.uint64(1)<<np.uint64(netids[net])
 # 0.75 mm centerline spacing reserve for any subsequently routed track.
 for x,y,z in path:
  for dy in range(-3,4):
   for dx in range(-3,4):
    if dx*dx+dy*dy<=10 and 0<=x+dx<N and 0<=y+dy<N:tracks[z,y+dy,x+dx]|=bit
 for u,v in zip(path,path[1:]):
  if u[2]!=v[2]:
   at=[v[0]*GRID,v[1]*GRID];vias.append((at,net))
   for dy in range(-4,5):
    for dx in range(-4,5):
     if dx*dx+dy*dy<=18:tracks[:,v[1]+dy,v[0]+dx]|=bit
 # exact center to lattice stub stays inside its own pad; retain every endpoint.
 pts=[(a['x'],a['y'],path[0][2])]+[(x*GRID,y*GRID,z) for x,y,z in path]+[(b['x'],b['y'],path[-1][2])]
 compact=[]
 for p in pts:
  if compact and p==compact[-1]:continue
  while len(compact)>=2:
   q,r=compact[-2:]
   cross=(r[0]-q[0])*(p[1]-r[1])-(r[1]-q[1])*(p[0]-r[0])
   if q[2]==r[2]==p[2] and abs(cross)<1e-9:compact.pop()
   else:break
  compact.append(p)
 for u,v in zip(compact,compact[1:]):
  if u[2]==v[2] and math.dist(u[:2],v[:2])>1e-7:segments.append((u[:2],v[:2],u[2],net,width(net)))

priority=['Net-(Q1-B)','/NEG','GND','+3V3','/DISP_MOSI','/DISP_SCK','/DC','/CS','/10','/LEFT','/RIGHT']
priority+=['Net-(D%d-K)'%i for i in range(1,7)]+['/TOP','/MID','/BOT']
if os.environ.get('ROUTE_PRIORITY'):priority=os.environ['ROUTE_PRIORITY'].split(',')
assert set(priority)==set(by), (set(by)-set(priority),set(priority)-set(by))
for net in priority:
 ps=by[net];connected=[ps[0]];todo=ps[1:]
 while todo:
  cand=sorted([(math.dist([a['x'],a['y']],[b['x'],b['y']]),ia,ib) for ia,a in enumerate(connected) for ib,b in enumerate(todo)])
  found=False
  for _,ia,ib in cand:
   a,b=connected[ia],todo[ib];path,n=route(net,a,b)
   if path:
    mark(net,path,a,b);connected.append(b);todo.pop(ib);report.append({'net':net,'from':a['ref']+':'+a['num'],'to':b['ref']+':'+b['num'],'expanded':n});found=True;break
  if not found:raise RuntimeError('UNROUTED '+net+' '+repr([(p['ref'],p['num']) for p in todo]))
 print(net,'routed',len(ps),'pads',flush=True)
# Retain original project metadata, strip old artwork and old copper.
out=[board[0]]+[copy.deepcopy(x) for x in board[1:] if isinstance(x,list) and x[0] not in ['footprint','segment','via','zone','gr_rect','gr_text','gr_line']]
out+=fps
out.append(['gr_rect',['start','0','0'],['end',str(SIZE),str(SIZE)],['stroke',['width','0.05'],['type','default']],['fill','no'],['layer',Q('Edge.Cuts')],['uuid',U()]])
for a,b,z,net,w in segments:out.append(['segment',['start',*map(str,a)],['end',*map(str,b)],['width',str(w)],['layer',Q('F.Cu' if z==0 else 'B.Cu')],['net',Q(net)],['uuid',U()]])
for at,net in vias:out.append(['via',['at',*map(str,at)],['size','0.7'],['drill','0.3'],['layers',Q('F.Cu'),Q('B.Cu')],['net',Q(net)],['uuid',U()]])
# Add ground plane with actual native v10 zone syntax based on existing zone.
zone=next(copy.deepcopy(z) for z in children(board,'zone') if get(z,'net')=='GND')
zone[:]=[x for x in zone if not(isinstance(x,list) and x[0] in ['filled_polygon','polygon','fill_segments'])]
child(zone,'uuid')[1]=U();child(zone,'layer')[1]=Q('B.Cu')
zone.append(['polygon',['pts',['xy','0.5','0.5'],['xy','94.5','0.5'],['xy','94.5','94.5'],['xy','0.5','94.5']]])
out.append(zone)
for ref in ['H1','H2','H3','H4']:
 x,y,_=P[ref]
 z=['zone',['net',Q('')],['layers',Q('F.Cu'),Q('B.Cu')],['uuid',U()],['name',Q('M3 '+ref+' 8mm copper clearance')],['hatch','edge','0.5'],['connect_pads',['clearance','0']],['min_thickness','0.25'],['keepout',['tracks','not_allowed'],['vias','not_allowed'],['pads','allowed'],['copperpour','not_allowed'],['footprints','allowed']],['fill',['thermal_gap','0.3'],['thermal_bridge_width','0.3']],['polygon',['pts',*([ 'xy',str(xx),str(yy)] for xx,yy in [(x-4,y-4),(x+4,y-4),(x+4,y+4),(x-4,y+4)])]]]
 out.append(z)
# Function labels on silkscreen outside switch bodies (short enough not to overlap).
for ref,(x,y) in centers.items():
 out.append(['gr_text',Q(labels[ref]),['at',str(x),str(y+8.2),'0'],['layer',Q('F.SilkS')],['uuid',U()],['effects',['font',['size','0.8','0.8'],['thickness','0.12']]]])
out.append(['gr_text',Q('JJK ALARM / COMPACT 95'),['at','47.5','42','0'],['layer',Q('F.SilkS')],['uuid',U()],['effects',['font',['size','1.0','1.0'],['thickness','0.15']]]])
# Per-pad copper assignments must be byte-for-byte equivalent as strings.
newmap={}
for f in fps:
 r=next(x[2] for x in children(f,'property') if x[1]=='Reference')
 newmap[str(r)]={str(p[1]):str(get(p,'net','')) for p in children(f,'pad') if p[1]}
assert oldmap==newmap
(OUT/'jjkspeakerpcb.kicad_pcb').write_text(dumps(out)+'\n')
for suffix in ['kicad_sch','kicad_pro']:(OUT/f'jjkspeakerpcb.{suffix}').write_bytes((ROOT/'PCB'/f'jjkspeakerpcb.{suffix}').read_bytes())
r={'board_dimensions_mm':[SIZE,SIZE,1.6],'original_dimensions_mm':[125,110,1.6],'preserved_pad_net_map':newmap,'positions':P,'switch_centers':centers,'switch_layout':{'top':['UP','TIME SET','SNOOZE'],'bottom':['DOWN','CLOCK SET','ALARM ON']},'tracks':len(segments),'vias':len(vias),'signal_track_width_mm':.25,'power_track_width_mm':.5,'segments':segments,'pads':pads,'connections':report,'native_validation_required':True}
(OUT.parent/'layout_and_routing.json').write_text(json.dumps(r,indent=2)+'\n')
print('DONE',len(segments),'segments',len(vias),'vias',OUT,flush=True)
