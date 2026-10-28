#!/usr/bin/env python3
"""Separate compact mechanical revision. Original shrine source is never overwritten.
Analytic electronics carrier and front panel; ornament kept as faceted source.
All units mm. Native PCB X right/Y down maps to assembly X right/Z down.
"""
from pathlib import Path
import cadquery as cq,numpy as np,trimesh,manifold3d as md,json,hashlib,time,sys
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'Build/Compact';O=W/'mechanical';O.mkdir(exist_ok=True)
P=O/'Parts';P.mkdir(exist_ok=True)
parts={};records={}
def box(x0,x1,y0,y1,z0,z1):return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
def cy(x,y0,z,r,h):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y0,z),cq.Vector(0,1,0))
def hexnut(x,y,z,depth=4):
 r=3.45
 pts=[cq.Vector(x+r*np.cos(np.pi/3*k),y,z+r*np.sin(np.pi/3*k)) for k in range(6)]
 wire=cq.Wire.makePolygon(pts+[pts[0]])
 return cq.Solid.extrudeLinear(wire,[],cq.Vector(0,depth,0))
def export(name,s,production=True):
 assert s.isValid(),name+' invalid'
 step=P/(name+'.step');stl=P/(name+'.stl');cq.exporters.export(s,str(step));cq.exporters.export(s,str(stl),tolerance=.04,angularTolerance=.15)
 m=trimesh.load(stl,force='mesh',process=True)
 records[name]={'valid_brep':True,'solid_count':len(s.Solids()),'mesh_watertight':bool(m.is_watertight),'dims_mm':m.extents.tolist(),'bounds_mm':m.bounds.tolist(),'production_part':production}
 parts[name]=s;return m
# Electronics carrier: open front at Y87, 3mm walls, removable face, PCB posts.
carrier=box(121,225,87,114,41.5,218.0).cut(box(124,222,86,111,44.5,215.0))
# Posts support only the four M3 mounting-hole keepout regions.
for x in (130.5,215.5):
 for z in (51,136):
  carrier=carrier.fuse(cy(x,104.6,z,4.5,6.4))
  carrier=carrier.cut(cy(x,102,z,1.7,14))
  # Rear-inserted square M3 nut pocket, 5.8mm across, 3mm deep into post.
  carrier=carrier.cut(hexnut(x,108,z,7))
  # Side-entry nut slot is reachable from the empty electronics cavity.
  if x<173:carrier=carrier.cut(box(x,x+6,108,110.9,z-3.05,z+3.05))
  else:carrier=carrier.cut(box(x-6,x,108,110.9,z-3.05,z+3.05))
# Front panel M3x16 fasteners at independent corner bosses.
front_bolts=[(125,45.5),(221,45.5),(125,212.5),(221,212.5)]
for x,z in front_bolts:
 carrier=carrier.fuse(box(x-5,x+5,87,97,z-5,z+5))
 carrier=carrier.cut(cy(x,83,z,1.7,16))
 # Nut slot opens toward interior for assembly.
 carrier=carrier.cut(hexnut(x,93,z,4.1))
# USB cable route, not an unverified panel connector footprint.
carrier=carrier.cut(box(136,154,110,115,142,154))
# Integral bridge behind cable for a 2.5mm nylon zip tie as strain relief.
anchor=box(135,155,106,111,157,163).cut(box(138,152,108,111.1,156,164))
carrier=carrier.fuse(anchor)
cm=export('Electronics_Carrier',carrier)
# Faceplate is removable. Front Y84, rear Y87.
face=box(120,226,84,87,40,220)
for x,z in front_bolts:face=face.cut(cy(x,83,z,1.7,5))
# Six 20.2mm square keycap apertures, 19.05mm horizontal pitch on PCB.
# Opening height must not create negative ligament; use 18.9mm width for
# 18.10mm kit DSA caps (0.40mm clearance each side), 20.2mm vertical.
for z in (81.,59.):face=face.cut(box(144.50,201.50,83,88,z-10.1,z+10.1))
# Screen viewing window intentionally larger than nominal active pixels,
# smaller than the 21.08 x 73.15mm module. Pocket is adjustable in Z.
face=face.cut(box(164,182,83,88,146.5,208.5))
# Display pocket rails. 0.5mm lateral clearance, optional shim thickness.
face=face.fuse(box(159.46,161.96,87,94,138.925,216.075))
face=face.fuse(box(184.04,186.54,87,94,138.925,216.075))
face=face.fuse(box(159.46,186.54,87,94,138.925,140.925))
# Removable top retention bar tabs; M3 bolts through, nuts accessible.
for x in (156,190):
 face=face.fuse(box(x-5,x+5,87,94,203.5,214.5))
 face=face.cut(cy(x,83,209,1.7,13))
# Buzzer vents align with actual BZ1 body center (X206.5,Z126).
for dx,dz in [(-3,-3),(0,-3),(3,-3),(-3,0),(0,0),(3,0),(-3,3),(0,3),(3,3)]:
 face=face.cut(cy(206.5+dx,83,126+dz,.85,5))
fm=export('Front_Panel',face)
# Rear retainer over upper module end; bolts to separate tabs, slots allow
# module height adjustment and shims, does not press the active LCD surface.
ret=box(151,195,94,98,203.5,214.5).fuse(box(162.5,183.5,91.2,94,208,212.4))
for x in (156,190):
 ret=ret.cut(cy(x,90,209,1.7,9))
 ret=ret.cut(hexnut(x,95,209,4))
rm=export('Display_Retainer',ret)
# Exact native PCB substrate transformed into case coords. Expand only Z to
# nominal finished1.6mm as mechanical envelope, keep original exported source.
board=cq.importers.importStep(str(W/'validated/CAD/PCB_Substrate.step')).val();bb=board.BoundingBox()
# Native export X0..95, Y-95..0,Z0..1.51; top Z141, frontY103.
M=cq.Matrix([[1,0,0,125.5],[0,0,-1.6/bb.zlen,104.6],[0,1,0,141],[0,0,0,1]])
board=board.transformGeometry(M)
bm=export('PCB_Finished_Envelope',board,False)
# Conservative component clearance references, not manufacturer CAD.
components=[]
def add(name,s):
 assert s.isValid();parts[name]=s;components.append((name,s))
# Switch housings and stems, keycaps supplied in kit (not tall original extensions).
for col,x in enumerate((153.95,173.,192.05)):
 for row,z in enumerate((81.,59.)):
  i=col*2+row+1
  add(f'SW{i}_MX_Body_Reference',box(x-7.8,x+7.8,91.4,103,z-7.8,z+7.8))
  add(f'SW{i}_MX_Stem_Reference',box(x-2,x+2,87.5,91.4,z-2,z+2))
  cap=box(x-9.05,x+9.05,79.5,88,z-9.05,z+9.05)
  add(f'SW{i}_Kit_Keycap_Reference',cap)
# Module/connector shapes with generous protection envelope inside case.
add('TFT_Module_Reference_21p08x73p15',box(162.46,183.54,87.0,90.7,140.925,214.075))
add('TFT_Jumper_Plugs_Clearance',box(163.0,183.0,90.7,107,142.2,144.7))
add('XIAO_and_Sockets_Reference',box(136.23,154.03,89.0,103,113.1,134.1))
add('BZ1_Reference',cy(206.5,93.5,126,6,9.5))
add('TFT_Header_Reference',box(166.96,187.28,94.5,103,127.7,130.3))
# Low-profile passives: conservative bodies above PCB, at actual pad midpoint.
layout=json.loads((W/'validated/layout_and_routing.json').read_text())
for ref,(px,py,angle) in layout['positions'].items():
 x=125.5+px;z=141-py
 if ref.startswith('D'):
  add(ref+'_Diode_Reference',box(x+2.1,x+5.5,100.0,103,z-1.4,z+1.4))
 elif ref.startswith('R'):
  add(ref+'_Resistor_Reference',box(x+.5,x+7.1,99.5,103,z-1.5,z+1.5))
 elif ref=='C1':add('C1_Reference',cy(x+1,92,z,2.5,11))
 elif ref=='C2':add('C2_Reference',box(x-.2,x+2.7,98,103,z-1.7,z+1.7))
 elif ref=='Q1':add('Q1_Reference',box(x-1.5,x+4,96,103,z-2.5,z+2.5))
# Source-faithful ornament plus a functional receiver. All transformations and
# material removals are intentional revision geometry, not a repair claim.
def to_md(m):
 v=np.asarray(m.vertices,np.float32);f=np.asarray(m.faces,np.uint32)
 mm=md.Mesh(v,f);mm.merge();a=md.Manifold(mm);assert a.status()==md.Error.NoError;return a
src=np.load(W/'shrine_printable.npz');a=md.Manifold(md.Mesh64(src['vertices'].astype(np.float64),src['faces'].astype(np.uint64)))
assert a.status()==md.Error.NoError
# Only the decorative skin is simplified within 0.5mm before exact new mounts
# and cutouts are created; no PCB/connector/drill geometry is scaled.
source_main=max(a.decompose(),key=lambda c:c.volume())
a=source_main
# Open front access for the removable electronics module. Leave existing scale.
cut=md.Manifold.cube((108,148,183)).translate((119,0,39))
ornament=a-cut
# Carrier geometry is merged structurally at the back and sides into ornament;
# remove any source material throughout the carrier cavity and cable tunnel.
outer=md.Manifold.cube((104,27,176.5)).translate((121,87,41.5))
# Preserve source only outside this carrier bounding box to prevent overlap.
ornament=ornament-outer
# Add rear brace rails to connect carrier into surviving source at Y>=148.
brace1=box(116,121,95,158,41.5,218.0);brace2=box(225,230,95,158,41.5,218.0)
# Side rails may create overlaps into original ornament deliberately; union.
brace=brace1.fuse(brace2);cq.exporters.export(brace,str(P/'_brace.stl'),tolerance=.04)
brm=trimesh.load(P/'_brace.stl',force='mesh',process=True)
body=ornament+to_md(cm)+to_md(brm)
# Cable channel connects electronics cavity to back exterior, avoiding PCB.
body=body-md.Manifold.cube((18,235,12)).translate((136,110,142))
assert body.status()==md.Error.NoError
# Remove zero-volume isolated fragments, preserve positive/negative cavity topology.
from mesh_cleanup import clean_degenerate
body=max(body.decompose(),key=lambda c:c.volume()).set_tolerance(1e-5)
mesh=body.to_mesh64();np.savez_compressed(O/'Body_Before_Cleanup.npz',vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts)
vv,ff,clean=clean_degenerate(mesh.vert_properties[:,:3],mesh.tri_verts)
mm=trimesh.Trimesh(vv,ff,process=False)
np.savez_compressed(O/'Body_Exact.npz',vertices=mm.vertices,faces=mm.faces)
mm.export(P/'Shrine_Body.stl')
check=trimesh.load(P/'Shrine_Body.stl',force='mesh',process=True)
assert check.is_watertight and check.is_winding_consistent, 'Final printable STL still contains touching/open shells'
# The small temporary brace input is not a production part.
(P/'_brace.stl').unlink()
# Nominal metal fasteners. These pass through intended holes; excluded from
# component collision tests because their seating contact is intentional.
fasteners=[]
for j,(x,z) in enumerate([(x,z) for x in (130.5,215.5) for z in (51,136)],1):
 screw=cy(x,100,z,3,3).fuse(cy(x,103,z,1.5,8))
 fasteners.append((f'PCB_M3x8_Screw_{j}',screw))
for j,(x,z) in enumerate(front_bolts+[(156,209),(190,209)],1):
 screw=cy(x,81,z,3,3).fuse(cy(x,84,z,1.5,16))
 fasteners.append((f'Panel_M3x16_Screw_{j}',screw))
for name,s in fasteners:parts[name]=s;cq.exporters.export(s,str(P/(name+'.stl')),tolerance=.05)
# Save component BREP compound for accurate STEP export, plus placed mesh views.
assembly=cq.Assembly(name='JJK_Compact_Internal_Assembly')
for name,s in parts.items():
 color=cq.Color(.1,.25,.13) if 'PCB' in name else cq.Color(.1,.1,.12)
 assembly.add(s,name=name,color=color)
assembly.save(str(O/'Electronics_Assembly.step'))
for name,s in components:cq.exporters.export(s,str(P/(name+'.stl')),tolerance=.05,angularTolerance=.15)
# Exact collision checks of the new analytic carrier and panel vs PCB/parts.
# Intentional display-to-front-lip contact and screw/nut interfaces excluded.
collisions=[]
for name,s in [('PCB',board)]+components:
 for host,hs in [('carrier',carrier),('front_panel',face)]:
  if name.startswith('TFT_Module') and host=='front_panel':continue
  vol=s.intersect(hs).Volume()
  if vol>1e-5:collisions.append({'part':name,'host':host,'overlap_mm3':vol})
report={'original_enclosure_sha256':hashlib.sha256((ROOT/'CAD/Owner_Originals/JJK_Alarm_Clock_Enclosure.stl').read_bytes()).hexdigest(),'original_preserved':True,'new_revision':True,'original_translation_mm':[-718.9990234375,-229.9998321533203,0],'new_PCB_size_mm':[95,95,1.6],'PCB_front_y_mm':103,'PCB_bounds_XZ_mm':[125.5,220.5,46,141],'keycap_row_aperture_mm':[57.0,20.2],'minimum_web_between_rows_mm':1.8,'kit_keycap_reference_mm':[18.10,18.10,8.5],'horizontal_switch_pitch_mm':19.05,'vertical_switch_pitch_mm':22,'TFT_module_reference_mm':[21.08,73.15,3.7],'display_size_is_reference_not_measurement':True,'display_rear_shim_gap_mm':0.5,'PCB_nuts_have_side_entry_slots':True,'M3_nut_pocket_across_flats_mm':float(6.9*np.cos(np.pi/6)),'back_cable_passage_mm':[18,12],'clearance_hardware_physical_tested':False,'source_STL_repaired_topology':True,'ornament_voxel_pitch_mm':1.0,'additional_ornament_simplification_tolerance_mm':0.0,'functional_geometry_built_after_remeshing':True,'decorative_body_triangles':len(mm.faces),'zero_area_mesh_repair':clean,'decorative_body_topological_watertight':bool(mm.is_watertight),'analytic_parts':records,'component_carrier_collision_checks':collisions,'old_extended_keycaps_preserved_but_not_used_on_compact_revision':True}
(O/'Mechanical_Report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
