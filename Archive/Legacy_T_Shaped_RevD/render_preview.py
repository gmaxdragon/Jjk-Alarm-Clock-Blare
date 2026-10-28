"""Render exact pad/trace/outline coordinates from generated native KiCad PCB.
Board data is source; this is NOT a KiCad 3D viewer screenshot.
"""
import runpy, os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as P, Circle, Rectangle
n=runpy.run_path(str(Path(__file__).parent/'build_board.py'))
O=n['OUTLINE'];parts=n['parts'];pads=n['PADS'];tracks=n['segments'];vias=n['vias'];target=n['target'];labels=n['BUTTONS']
fig, ax=plt.subplots(figsize=(11,11),dpi=185)
fig.patch.set_facecolor('#08090E');ax.set_facecolor('#08090E')
ax.add_patch(P(O,closed=True,facecolor='#151C26',edgecolor='#DF2B36',linewidth=4))
for a,b,ly,net in tracks:
 col='#E34A44' if ly=='F.Cu' else '#3393EC'; ax.plot([a[0],b[0]],[a[1],b[1]],lw=1.0,color=col,alpha=.8,zorder=2)
for q in pads:
 x,y=q['at'];siz=q['size'];s=max(siz) if isinstance(siz,tuple) else siz
 if q['role']=='np_thru_hole':
  ax.add_patch(Circle((x,y),s/2,facecolor='#05080E',edgecolor='#737F91',lw=.6,zorder=5));continue
 c='#B4AA81' if q['role']=='smd' else '#E6B65F'
 ax.add_patch(Circle((x,y),s/2,facecolor=c,edgecolor='#ECE2AD',lw=.2,zorder=4))
 if q['role']=='thru_hole':ax.add_patch(Circle((x,y),q['drill']/2,facecolor='#080A0C',edgecolor='none',zorder=5))
for a,net in vias:
 ax.add_patch(Circle(a,.35,facecolor='#F5DFAD',edgecolor='#41270D',lw=.6,zorder=6))
for ref,name,cx,cy,*_ in labels:
 ax.add_patch(Rectangle((cx-9.525,cy-9.525),19.05,19.05,facecolor='#251C26',edgecolor='#DD3844',linewidth=1.15,zorder=7))
 ax.add_patch(Circle((cx,cy),6,facecolor='#0B0C16',edgecolor='#941E27',lw=2,zorder=8))
 ax.text(cx,cy,{'SNOOZE':'SNOOZE','UP':'▲','DOWN':'▼','BACK':'↶','SKIP':'SKIP','OK':'OK'}.get(name,name),ha='center',va='center',color='#FEF6E5',size=11 if name!='SNOOZE' else 7,zorder=9,fontweight='bold')
for p in parts:
 if p['ref']=='U1':
  ax.add_patch(Rectangle((39.1,72),17.8,21,fill=False,ec='#82A7BB',ls=':',lw=1.5,zorder=7));ax.text(48,84,'XIAO C3\nBACK',color='#9BCEDC',va='center',ha='center',size=8,zorder=8)
 if p['ref']=='BZ1':
  ax.add_patch(Circle((48,43),6,facecolor='#131E29',edgecolor='#8BBAD4',lw=1,zorder=7));ax.text(48,43,'BZ\nBACK',ha='center',va='center',size=7,color='white',zorder=8)
 if p['ref']=='J1':
  ax.text(48,6.4,'TFT 8-PIN / BACK',ha='center',va='center',color='#C9AABB',size=7,zorder=10)
ax.plot([32.5,63.5,63.5,32.5,32.5],[18,18,83,83,18],color='#E29F31',lw=1.15,ls='--',zorder=10)
ax.text(48,38.7,'TFT\nSCREEN\nZONE',ha='center',va='center',color='#FFDDD6',fontsize=13,zorder=10,fontweight='bold')
ax.text(48,52,'76 × 284 PX',ha='center',va='center',color='#BBA5B1',fontsize=7,zorder=10)
ax.set_xlim(-4,100);ax.set_ylim(100,-4);ax.set_aspect('equal');ax.axis('off')
ax.set_title('GGK ALARM  •  KiCad PCB geometry preview  •  96 × 95 mm',color='#F4D5D5',fontsize=16,pad=20)
plt.tight_layout()
out=Path(__file__).parent/'Preview'/'GGK_Alarm_KiCad_PCB_Geometry_Preview.png';fig.savefig(out,dpi=185,facecolor=fig.get_facecolor(),bbox_inches='tight')
print(out,out.stat().st_size)
