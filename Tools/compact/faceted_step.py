"""Write ISO 10303-21 faceted BREP from oriented closed indexed triangle meshes.
No extension renaming. Units are mm; each component has its own product/root.
"""
from pathlib import Path
import numpy as np
class Step:
 def __init__(self):self.lines=[]
 def add(self,s):self.lines.append(s);return len(self.lines)
 def ref(self,n):return '#'+str(n)
 def seq(self,ns):return '('+','.join(map(self.ref,ns))+')'
 def write(self,path):
  Path(path).write_text("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('JJK Alarm faceted solid assembly'),'2;1');\nFILE_NAME('JJK Alarm','2026-10-27T00:00:00',('Vivaan Goel'),(''),'JJK Alarm mesh conversion','Open design','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n"+''.join(f'#{i}={s};\n' for i,s in enumerate(self.lines,1))+"ENDSEC;\nEND-ISO-10303-21;\n")
def export(parts,path):
 S=Step();ref=S.ref;seq=S.seq
 app=S.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
 S.add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{ref(app)})")
 mm=S.add('(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))')
 rad=S.add('(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))')
 sr=S.add('(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())')
 tol=S.add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-06),{ref(mm)},'distance_accuracy_value','')")
 ctx=S.add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({ref(tol)})) GLOBAL_UNIT_ASSIGNED_CONTEXT({seq([mm,rad,sr])}) REPRESENTATION_CONTEXT('','3D mm'))")
 pc=S.add(f"PRODUCT_CONTEXT('',{ref(app)},'mechanical')");dc=S.add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{ref(app)},'design')")
 normals={};planes={}
 for name,verts,faces in parts:
  name=name.replace("'",'')
  vs=[S.add("CARTESIAN_POINT('',("+','.join((f'{float(v):.9f}'.rstrip('0') if '.' in f'{float(v):.9f}' else f'{float(v):.9f}') for v in p)+'))') for p in verts]
  fs=[]
  for f in faces:
   loop=S.add(f"POLY_LOOP('',{seq(vs[int(i)] for i in f)})")
   bd=S.add(f"FACE_OUTER_BOUND('',{ref(loop)},.T.)")
   p0,p1,p2=np.asarray(verts)[f];n=np.cross(p1-p0,p2-p0);norm=np.linalg.norm(n)
   if norm<1e-16:raise ValueError('Degenerate triangle in '+name)
   n=n/norm;nk=tuple(np.round(n,10));pk=(*nk,round(float(np.dot(n,p0)),8))
   if pk not in planes:
    if nk not in normals:normals[nk]=S.add("DIRECTION('',("+','.join(f'{float(v):.10f}'.rstrip('0') for v in n)+'))')
    nr=normals[nk]
    ax=S.add(f"AXIS2_PLACEMENT_3D('',{ref(vs[int(f[0])])},{ref(nr)},$)")
    planes[pk]=S.add(f"PLANE('',{ref(ax)})")
   pl=planes[pk]
   fs.append(S.add(f"FACE_SURFACE('',({ref(bd)}),{ref(pl)},.T.)"))
  shell=S.add(f"CLOSED_SHELL('{name}',{seq(fs)})")
  brep=S.add(f"FACETED_BREP('{name}',{ref(shell)})")
  rep=S.add(f"FACETED_BREP_SHAPE_REPRESENTATION('{name}',({ref(brep)}),{ref(ctx)})")
  p=S.add(f"PRODUCT('{name}','{name}','',({ref(pc)}))")
  pf=S.add(f"PRODUCT_DEFINITION_FORMATION('','',{ref(p)})")
  pd=S.add(f"PRODUCT_DEFINITION('design','',{ref(pf)},{ref(dc)})")
  ps=S.add(f"PRODUCT_DEFINITION_SHAPE('','',{ref(pd)})")
  S.add(f"SHAPE_DEFINITION_REPRESENTATION({ref(ps)},{ref(rep)})")
  S.add(f"PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({ref(p)}))")
 S.write(path)
