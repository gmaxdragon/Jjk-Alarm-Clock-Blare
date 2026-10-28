#!/usr/bin/env python3
"""Export six keycaps and validate geometry without scaling electrical parts.
This is not a complete-clock assembly builder. It preserves the owner's geometry.
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
 # Move superseded four-part exports out of the current production directory.
 legacy=ROOT/'CAD/Recovered/Original_Keycap_STL';legacy.mkdir(parents=True,exist_ok=True)
 for p in production.glob('Extended_Keycap_*.stl'):shutil.move(str(p),str(legacy/p.name))
 native=out/'PCB_Drilled_Body.step'
 board=cq.importers.importStep(str(native)).solids().vals()
 assert len(board)==1 and board[0].isValid()
 dims=np.array(bbox(board[0])[3:])-np.array(bbox(board[0])[:3])
 assert np.allclose(dims,[125,110,1.6],atol=0.0001),dims
 data={'PCB_dimensions_mm':dims.tolist(),'PCB_STEP_reimport_valid':True,'PCB_STEP_bounds_mm':bbox(board[0]),'PCB_rescaled':False,'PCB_layout_changed':False,'keycap_source_sha256':sha(source),'six_keycap_STEP_solids':6,'keycap_parts':records,'first_to_last_switch_center_mm':95.25,'switch_pitch_mm':19.05,'six_keycap_row_width_mm':95.25+max(x['dimensions_mm'][0] for x in records),'keycap_row_depth_mm':max(x['dimensions_mm'][1] for x in records),'complete_clock_assembly':False,'physical_fit_tested_by_this_script':False,'under_100mm_PCB_requirement_met':False}
 checks=ROOT/'CAD/Checks';checks.mkdir(parents=True,exist_ok=True)
 (checks/'Current_Mechanical_Exports.json').write_text(json.dumps(data,indent=2)+'\n')
 with zipfile.ZipFile(ROOT/'CAD/JJK_Alarm_Corrected_Parts.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(out.glob('*')):
   if p.is_file():z.write(p,'References/'+p.name)
  for p in sorted(production.glob('Keycap_*')):z.write(p,'Keycaps/'+p.name)
  z.write(checks/'Current_Mechanical_Exports.json','Checks/Current_Mechanical_Exports.json')
 print('PASS: native PCB STEP reimport; six keycap STEP solids and six watertight STL parts. No enclosure-fit claim.')
if __name__=='__main__':main()
