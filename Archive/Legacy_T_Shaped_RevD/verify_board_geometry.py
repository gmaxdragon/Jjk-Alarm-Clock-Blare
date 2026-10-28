#!/usr/bin/env python3
"""Design-only checks: positive KiCad DRC is still required before fabrication.

Checks actual coordinates before/after PCB file generation, relevant spacing,
size cap, lower six-switch rail geometry, mechanical top module envelope,
missing routed nets and that no key legends are on silkscreen.
"""
from __future__ import annotations
import json,re,os,runpy,itertools
from collections import defaultdict
from pathlib import Path
from shapely.geometry import box, Point, LineString, Polygon
from shapely.strtree import STRtree
ROOT=Path(__file__).parent
n=runpy.run_path(str(ROOT/'build_board.py'))
parts=n['parts'];pads=n['PADS'];out=n['POLY'];segments=n['segments'];vias=n['vias'];routing=n['routing_report'];
violations=[]
conductors={0:[],1:[]}
for q in pads:
 if q['role']=='np_thru_hole':continue
 x,y=q['at'];ww,hh=q['size'] if isinstance(q['size'],tuple) else(q['size'],q['size'])
 g=box(x-ww/2,y-hh/2,x+ww/2,y+hh/2) if q['role']=='smd' else Point(x,y).buffer(ww/2, resolution=30)
 for layer in ([1] if q['role']=='smd' else [0,1]):
  conductors[layer].append((g,q['net'],'pad '+q['part']+':'+q['number']))
for idx,(a,b,layer,net) in enumerate(segments):
 g=LineString([a,b]).buffer(.125, cap_style=1,resolution=8)
 conductors[0 if layer=='F.Cu' else 1].append((g,net,'track '+str(idx)))
for idx,(point,net) in enumerate(vias):
 for layer in (0,1): conductors[layer].append((Point(point).buffer(.35, resolution=30),net,'via '+str(idx)))
closest=100
for layer,items in conductors.items():
 geoms=[x[0] for x in items]
 tree=STRtree(geoms)
 for i,gi in enumerate(geoms):
  edge=out.boundary.distance(gi)
  if edge < 0.22:
   violations.append(('EDGE',layer,items[i][2],round(edge,4)))
  for j in tree.query(gi.buffer(.22)):
   j=int(j)
   if j<=i or items[i][1]==items[j][1]:continue
   d=gi.distance(geoms[j]);closest=min(d,closest)
   if d<.2-1e-5: violations.append(('CLEARANCE',layer,items[i][2],items[j][2],round(d,4)))

switches=[p for p in parts if p['ref'].startswith('SW')]
switches.sort(key=lambda p:int(p['ref'][2:]))
positions=[(round(p['x']-2.54,4),round(p['y']+5.08,4)) for p in switches]
pitches=[round(b[0]-a[0],3) for a,b in zip(positions,positions[1:])]
assert len(switches)==6 and all(abs(a[1]-89.5)<.001 for a in positions)
assert all(abs(d-15.9)<.01 for d in pitches),pitches
assert out.bounds == (0.35,0.35,99.65,99.65)
assert len([x for x in routing if x['status']=='UNROUTED'])==0
assert not violations,violations[:20]
actual= (ROOT/'PCB/jjkspeakerpcb.kicad_pcb').read_text()
# No visible physical SW names or prints are allowed on either production silk.
assert not re.search(r'\(gr_text "(?:UP|DOWN|TIME SET|CLOCK SET|SNOOZE|ALARM ON)"',actual)
for ref in ['SW1','SW2','SW3','SW4','SW5','SW6']:
 fragment=actual.split('(fp_text reference "'+ref+'"',1)[1].split('\n',1)[0]
 assert '(layer "F.Fab")' in fragment,fragment
for sym in ['3V3','GND','DISP_SCK','DISP_MOSI','DISP_DC','DISP_CS','PIEZO']:
 assert sym in actual
for padno in range(15,23):
 assert f'(pad "{padno}" smd' in actual,('XIAO_BACK_PAD_MISSING',padno)
assert '(layer "Dwgs.User")' in actual
assert 'no decorative' not in actual # source text only, no board art silkscreen

# Practical warning: standard 18mm DSA caps collide at 15.9mm pitch.
report={
 'revision':'GGK Rev C / no-art T-shape / alternate boot-safe matrix',
 'geometry_check_result':'PASS: 0 unrouted signal groups, 0 clearance violations <0.20 mm in geometric check',
 'not_native_kicad_drc':True,
 'board_outline_width_mm':99.3,'board_outline_height_mm':99.3,
 'board_copper_substrate_area_mm2':round(out.area,2),
 'area_reduction_vs_revA_pct':round(100*(1-out.area/7293.0),1),
 'switch_count':len(switches),
 'switch_physical_layout':'single 1x6 straight row',
 'switch_centers_xy_mm':positions,
 'key_pitch_mm':15.9,
 'standard_dsa_1u_keycaps_fit':False,
 'required_narrow_custom_keycap_width_mm':15.4,
 'actual_mx_switch_housing_mm_estimate':15.6,
 'key_body_fit_must_be_physically_tested':True,
 'display':'portrait 76 x 284 ST7789; example breakout body 21.08 x 73.15mm',
 'display_module_dimensions_must_be_verified':True,
 'display_is_separate_and_connected_by_8pin_cable':True,
 'xiao_esp32c3': 'back mount, top USB-C, 22 electrical/mechanical contacts modeled',
 'buzzer_driver_requires_exact_kit_part_verification':True,
 'power':'USB-C power bank or regulated USB-C; no added cell/RTC, powerbank must remain on',
 'embedded_backup_timekeeping_on_power_failure':False,
 'smartphone_sync_possible_over_wifi':True,
 'display_contents_editable_in_firmware':True,
 'traces':len(segments),'vias':len(vias),
 'clearance_violations_0p2mm':len(violations),
 'unrouted_signal_groups':0,
 'copper_ground_zones':'GND wired explicitly plus unfilled zones; KiCad native refill required',
 'manufacturing_approval':False,
 'native_kicad_erc_and_drc':'NOT YET RUN',
}
(ROOT/'Docs'/'geometry_check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
