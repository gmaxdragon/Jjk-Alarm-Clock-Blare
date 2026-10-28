#!/usr/bin/env python3
"""Export six keycaps and validate geometry without scaling electrical parts.
The finished-board size envelope is distinct from KiCad's dielectric-only body.
This is not a complete-clock assembly builder.
"""
from pathlib import Path
import hashlib,json,shutil,zipfile
import cadquery as cq
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bbox(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def main():
 out=ROOT/'CAD/Current_References';out.mkdir(parents=True,exist_ok=True)
 production=ROOT/'Production/Case_Parts';production.mkdir(parents=True,exist_ok=True)
 source=ROOT/'CAD/Recovered/Keycaps_Recovered.step'
 caps=cq.importers.importStep(str(source)).solids().vals()
 assert len(caps)==4 and all(s.isValid() for s in caps)
 caps.sort(key=lambda s:(bbox(s)[0],bbox(s)[1]))
 records=[];layout=[]
 for i in range(6):
  s=caps[i%4];b=bbox(s);s=s.translate((-b[0],-b[1],-b[2]))
  step=production/f'Keycap_{i+1:02d}.step';stl=production/f'Keycap_{i+1:02d}.stl'
  cq.exporters.export(s,str(step));cq.exporters.export(s,str(stl),tolerance=0.01,angularTolerance=0.1)
  imported=cq.importers.importStep(str(step)).solids().vals()
  assert len(imported)==1 and imported[0].isValid()
  mesh=trimesh.load(stl,force='mesh',process=True)
  assert mesh.is_watertight and mesh.is_winding_consistent
  assert abs(imported[0].Volume()-s.Volume())<0.001
  layout.append(s.translate(((i%3)*22,(i//3)*22,0)))
  records.append({'position':i+1,'source_body':i%4+1,'duplicate_of_position':i-3 if i>=4 else None,'dimensions_mm':mesh.extents.tolist(),'valid_STEP_solid':True,'STL_watertight':True,'internal_cavity_shells':len(imported[0].Shells())-1,'volume_mm3':imported[0].Volume(),'step_sha256':sha(step),'stl_sha256':sha(stl)})
 combined=out/'Six_Keycaps.step';cq.exporters.export(cq.Compound.makeCompound(layout),str(combined))
 test=cq.importers.importStep(str(combined)).solids().vals()
 assert len(test)==6 and all(s.isValid() for s in test)
 legacy=ROOT/'CAD/Recovered/Original_Keycap_STL';legacy.mkdir(parents=True,exist_ok=True)
 for p in production.glob('Extended_Keycap_*.stl'):shutil.move(str(p),str(legacy/p.name))
 native=out/'PCB_Drilled_Body.step'
 board=cq.importers.importStep(str(native)).solids().vals()
 assert len(board)==1 and board[0].isValid()
 bb=bbox(board[0]);dims=np.array(bb[3:])-np.array(bb[:3])
 assert np.allclose(dims[:2],[125,110],atol=0.0001),dims
 assert 1.4<dims[2]<1.7,dims
 # KiCad's export omits copper/mask when exporting only the substrate.
 # Preserve that exact native model. Add an explicitly named nominal envelope
 # for enclosure design: same XY/drill centers, Z alone extended to 1.6 mm.
 nominal=json.loads((ROOT/'CAD/Checks/Native_PCB_Dimensions.json').read_text())['nominal_thickness_mm']
 ratio=nominal/float(dims[2])
 env=board[0].transformGeometry(cq.Matrix([[1,0,0,0],[0,1,0,0],[0,0,ratio,-bb[2]*ratio],[0,0,0,1]]))
 assert env.isValid() and len(env.Solids())==1
 envelope=out/'PCB_Finished_Size_Envelope.step';cq.exporters.export(env,str(envelope))
 ei=cq.importers.importStep(str(envelope)).solids().vals()
 assert len(ei)==1 and ei[0].isValid()
 eb=bbox(ei[0]);ed=np.array(eb[3:])-np.array(eb[:3])
 assert np.allclose(ed,[125,110,nominal],atol=0.0001),ed
 cq.exporters.export(ei[0],str(out/'PCB_Finished_Size_Envelope.stl'),tolerance=0.02,angularTolerance=0.1)
 data={'PCB_XY_dimensions_mm':dims[:2].tolist(),'PCB_native_substrate_thickness_mm':float(dims[2]),'PCB_nominal_finished_thickness_mm':nominal,'PCB_STEP_reimport_valid':True,'PCB_STEP_bounds_mm':bb,'finished_size_envelope_dimensions_mm':ed.tolist(),'finished_size_envelope_reimport_valid':True,'finished_envelope_method':'Native drilled substrate, Z-only expansion to nominal finished thickness; not a copper-layer model','PCB_XY_rescaled':False,'PCB_layout_changed':False,'keycap_source_sha256':sha(source),'six_keycap_STEP_solids':6,'keycap_parts':records,'first_to_last_switch_center_mm':95.25,'switch_pitch_mm':19.05,'six_keycap_row_width_mm':95.25+max(x['dimensions_mm'][0] for x in records),'keycap_row_depth_mm':max(x['dimensions_mm'][1] for x in records),'complete_clock_assembly':False,'physical_fit_tested_by_this_script':False,'under_100mm_PCB_requirement_met':False}
 checks=ROOT/'CAD/Checks';checks.mkdir(parents=True,exist_ok=True)
 (checks/'Current_Mechanical_Exports.json').write_text(json.dumps(data,indent=2)+'\n')
 with zipfile.ZipFile(ROOT/'CAD/JJK_Alarm_Corrected_Parts.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(out.glob('*')):
   if p.is_file():z.write(p,'References/'+p.name)
  for p in sorted(production.glob('Keycap_*')):z.write(p,'Keycaps/'+p.name)
  for p in sorted(checks.glob('*')):
   if p.name in ('Current_Mechanical_Exports.json','Native_PCB_Dimensions.json','Latest_STL_Uploads.json','ERC_After_Export.rpt','DRC_After_Export.rpt'):z.write(p,'Checks/'+p.name)
 print('PASS: native PCB substrate, 1.6 mm finished size envelope, six keycap STEP solids and six watertight STL parts. No complete-enclosure claim.')
if __name__=='__main__':main()
