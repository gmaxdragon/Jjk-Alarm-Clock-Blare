#!/usr/bin/env python3
"""Faithful geometry preview of generated native KiCad PCB (NOT a photoreal AI image).

Reads build_board.py's actual plot coordinates. Front view displays actual PCB
silkscreen blank at each key; optional translucent portrait screen is a CAD
placement reference on the non-fabrication Dwgs.User layer.
"""
import os, runpy
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
P=Path(__file__).parent
obj=runpy.run_path(str(P/'build_board.py'))
outline=obj['OUTLINE'];parts=obj['parts'];pads=obj['PADS'];segments=obj['segments'];vias=obj['vias']
fig,ax=plt.subplots(figsize=(9.6,9.5),dpi=170)
fig.patch.set_facecolor('#edf1f5');ax.set_facecolor('#edf1f5')
ax.add_patch(Polygon(outline,closed=True,facecolor='#142b29',edgecolor='#061716',linewidth=2.2,zorder=1))
# The original front silkscreen has no illustration and no key legends.
for a,b,layer,net in segments:
    col='#EFA35B' if layer=='F.Cu' else '#7AC3E8'
    ax.plot((a[0],b[0]),(a[1],b[1]),color=col,lw=1.10,alpha=.8 if layer=='F.Cu' else .42,zorder=2)
for at,net in vias:
    ax.add_patch(Circle(at,.40,edgecolor='#fff7df',facecolor='#cc9930',lw=.8,zorder=6))
for q in pads:
    x,y=q['at'];w,h=q['size'] if isinstance(q['size'],tuple) else(q['size'],q['size'])
    if q['role']=='np_thru_hole':
        ax.add_patch(Circle((x,y),w/2,edgecolor='#8fada5',facecolor='#edf1f5',lw=.85,zorder=7))
        continue
    if q['role']=='smd':
        ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#b4ae69',edgecolor='#fff0b8',lw=.25,zorder=5))
    else:
        ax.add_patch(Circle((x,y),w/2,facecolor='#dcb75e',edgecolor='#fff4cc',lw=.28,zorder=5))
        ax.add_patch(Circle((x,y),q['drill']/2,facecolor='#061716',edgecolor='#fff4cc',lw=.13,zorder=6))

# Physical MX top housing approx 15.6mm; outlines only, NO key labels on PCB.
for p in parts:
    if p['ref'].startswith('SW'):
        cx=p['x']-2.54;cy=p['y']+5.08
        ax.add_patch(Rectangle((cx-7.8,cy-7.8),15.6,15.6,facecolor='#183937',edgecolor='#a9b9af',lw=1.0,zorder=8))
        ax.add_patch(Circle((cx,cy),4.1,facecolor='#243f3d',edgecolor='#e1e5d9',lw=.7,zorder=9))
        # MX cruciform switch stem, generic footprint reference, not a printed key label.
        ax.add_patch(Rectangle((cx-2.8,cy-.6),5.6,1.2,facecolor='#b1c6b8',edgecolor='none',zorder=10))
        ax.add_patch(Rectangle((cx-.6,cy-2.8),1.2,5.6,facecolor='#b1c6b8',edgecolor='none',zorder=10))
    if p['ref']=='U1':
        ax.add_patch(Rectangle((41.1,2),17.8,21.0,facecolor='none',edgecolor='#ffe99b',lw=1.15,ls=(0,(3,2)),zorder=10))
        ax.text(50,11,'XIAO\n(back)',color='#eed28f',fontsize=7,ha='center',va='center',zorder=11)
    if p['ref']=='BZ1':
        ax.add_patch(Circle((50,46),6.0,facecolor='none',edgecolor='#d6dfb7',lw=1,ls=(0,(4,2)),zorder=8))
        ax.text(50,46,'PIEZO\n(back)',color='#f5f4cb',fontsize=6.5,ha='center',va='center',zorder=9)
    if p['ref']=='J1':
        ax.add_patch(Rectangle((39.3,65.6),21,3,edgecolor='#dddb8f',facecolor='none',lw=1.1,ls='--',zorder=8))

# Mechanical REF ONLY, identical bounds are in actual KiCad Dwgs.User:
ax.add_patch(Rectangle((39.46,1.15),21.08,73.15,facecolor='#222a36',alpha=.55,edgecolor='#eee0ca',lw=1.4,ls='--',zorder=7))
ax.add_patch(Rectangle((42.4,11.6),15.2,55.3,facecolor='#0c1521',alpha=.85,edgecolor='#94a7ba',lw=.9,zorder=7))
ax.text(50,33,'PORTRAIT\nTFT',color='#f1ebde',fontsize=11,ha='center',va='center',zorder=10,fontweight='bold')
ax.text(50,39,'76 × 284',color='#abbec6',fontsize=7,ha='center',va='center',zorder=10)
ax.text(50,-3.5,'USB-C ↑',fontsize=10,ha='center',fontweight='bold',color='#1f3047')
ax.add_patch(Rectangle((46.4,-.65),7.2,2.4,facecolor='#839aa3',edgecolor='#213b44',zorder=12))
ax.set_aspect('equal');ax.set_xlim(-5,105);ax.set_ylim(105,-8)
ax.axis('off')
fig.suptitle('GGK ALARM • Rev C • REAL KiCad geometry',fontsize=17,fontweight='bold',color='#12262a')
fig.text(.5,.05,'T-shaped board   •   99.3 × 99.3 mm   •   1×6 MX row   •   no decorative images or key legends',ha='center',fontsize=10,color='#334b53')
fig.text(.5,.026,'Blue: back copper  |  Orange: front copper  |  TFT drawing: reference only, not a fabricated display',ha='center',fontsize=9,color='#526b73')
fig.subplots_adjust(top=.94,bottom=.10,left=.035,right=.965)
out=P/'Preview'/'GGK_Alarm_RevC_KiCad_PCB_Layout.png';out.parent.mkdir(exist_ok=True)
fig.savefig(out,dpi=175,facecolor=fig.get_facecolor())
plt.close(fig)
print(out, out.stat().st_size)
