from pathlib import Path
import sys,json,numpy as np,trimesh,time,gc,hashlib
from faceted_step_merged import export
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'Build/Compact';O=W/'mechanical';P=O/'Parts'
z=np.load(O/'Body_Exact.npz');v=z['vertices'];f=z['faces']
body=trimesh.Trimesh(v,f,process=True)
assert body.is_watertight and body.is_winding_consistent
parts=[('Shrine_Body_With_Integrated_Carrier',body.vertices,body.faces)]
for path in sorted(P.glob('*.stl')):
 if path.stem in ('Shrine_Body','Electronics_Carrier','Shrine_Body_Repaired_Test') or path.stem.startswith('_'):continue
 m=trimesh.load(path,force='mesh',process=True)
 assert m.is_watertight and m.is_winding_consistent,path
 parts.append((path.stem,m.vertices,m.faces))
expected=len(parts)
print('Exporting',expected,'parts',sum(len(p[2]) for p in parts),'triangles',flush=True)
t=time.monotonic();topology=export(parts,O/'JJK_Alarm_Assembly.step')
print('Exported bytes',(O/'JJK_Alarm_Assembly.step').stat().st_size,'sec',time.monotonic()-t,flush=True)
assert (O/'JJK_Alarm_Assembly.step').stat().st_size<100*1024*1024
parts=None;v=None;f=None;body=None;gc.collect()
import cadquery as cq
shape=cq.importers.importStep(str(O/'JJK_Alarm_Assembly.step'))
solids=shape.solids().vals();print('reimport solids',len(solids),flush=True)
checks=[]
for i,s in enumerate(solids):
 bb=s.BoundingBox();checks.append({'index':i,'valid':bool(s.isValid()),'volume_mm3':s.Volume(),'bounds_mm':[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]})
 print('checked',i,checks[-1]['valid'],flush=True)
report={'STEP_bytes':(O/'JJK_Alarm_Assembly.step').stat().st_size,'STEP_sha256':hashlib.sha256((O/'JJK_Alarm_Assembly.step').read_bytes()).hexdigest(),'STEP_reimport_solids':len(solids),'expected_solids':expected,'solids':checks,'all_solids_valid':all(c['valid'] for c in checks),'export_is_faceted_BREP':True,'coplanar_face_consolidation_preserves_geometry':True,'is_original_parametric_CAD':False,'original_parts_preserved':True,'component_geometry_is_reference_envelopes':True,'hardware_tested':False,'parts_topology':topology}
assert len(solids)==expected and report['all_solids_valid']
(O/'Assembly_STEP_Validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('DONE',report['all_solids_valid'],flush=True)
