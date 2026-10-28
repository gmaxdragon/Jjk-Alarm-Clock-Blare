#!/usr/bin/env python3
"""Use the native KiCad API for exact PCB dimensions and drilling coordinates."""
from pathlib import Path
import csv,hashlib,json
import pcbnew
root=Path(__file__).resolve().parents[1];src=root/'PCB/jjkspeakerpcb.kicad_pcb'
b=pcbnew.LoadBoard(str(src))
# This source has one rectangular Edge.Cuts drawing. The graphic bounding box
# includes its 0.05 mm stroke; routed dimensions use the drawing centerline.
edges=[d for d in b.GetDrawings() if d.GetLayer()==pcbnew.Edge_Cuts]
assert len(edges)==1, 'Expected the single rectangular outline in the supplied PCB'
a=edges[0].GetStart();z=edges[0].GetEnd()
x0=pcbnew.ToMM(min(a.x,z.x));y0=pcbnew.ToMM(min(a.y,z.y))
w=pcbnew.ToMM(abs(z.x-a.x));h=pcbnew.ToMM(abs(z.y-a.y))
assert abs(w-125)<0.0001 and abs(h-110)<0.0001,(w,h)
out=root/'CAD/Current_References';out.mkdir(parents=True,exist_ok=True)
parts=[];holes=[];switches=[]
for f in b.GetFootprints():
 ref=f.GetReference();pos=f.GetPosition()
 parts.append([ref,str(f.GetFPID().GetLibItemName()),pcbnew.ToMM(pos.x)-x0,pcbnew.ToMM(pos.y)-y0,f.GetOrientationDegrees()])
 for p in f.Pads():
  d=p.GetDrillSize()
  if d.x<=0:continue
  pos=p.GetPosition();x=pcbnew.ToMM(pos.x)-x0;y=pcbnew.ToMM(pos.y)-y0
  holes.append([ref,p.GetNumber(),x,y,pcbnew.ToMM(d.x),pcbnew.ToMM(d.y),str(p.GetAttribute())])
  if ref.startswith('SW') and abs(pcbnew.ToMM(d.x)-4)<0.001:switches.append([ref,x,y])
for t in b.GetTracks():
 if isinstance(t,pcbnew.PCB_VIA):
  p=t.GetPosition();d=pcbnew.ToMM(t.GetDrillValue());holes.append(['VIA','',pcbnew.ToMM(p.x)-x0,pcbnew.ToMM(p.y)-y0,d,d,'via'])
for filename,head,rows in [('Component_Positions_mm.csv',['Reference','Footprint','X_from_left_mm','Y_from_top_mm','Rotation_deg'],parts),('Drill_Positions_mm.csv',['Reference','Pad','X_from_left_mm','Y_from_top_mm','Drill_X_mm','Drill_Y_mm','Pad_type'],holes)]:
 with (out/filename).open('w',newline='') as f:
  wr=csv.writer(f);wr.writerow(head);wr.writerows(sorted(rows,key=lambda r:(r[0],str(r[1]))))
(root/'CAD/Checks/Native_PCB_Dimensions.json').write_text(json.dumps({'width_mm':w,'height_mm':h,'nominal_thickness_mm':pcbnew.ToMM(b.GetDesignSettings().GetBoardThickness()),'origin_KiCad_mm':[x0,y0],'dimension_method':'Edge.Cuts centerline endpoints; excludes drawing stroke width','switch_centers_mm':sorted(switches),'drill_count':len(holes),'PCB_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'PCB_modified':False},indent=2)+'\n')
print('Native board geometry:',w,h,'mm;',len(holes),'drills')
