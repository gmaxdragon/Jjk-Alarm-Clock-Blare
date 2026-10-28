"""Exact coplanar-face consolidation for a genuine AP214 faceted STEP.
Preserves oriented vertices and holes; never changes units or scales the meshes.
"""
from pathlib import Path
import numpy as np,trimesh
from faceted_step import Step

def face_groups(vertices, triangles):
    m=trimesh.Trimesh(vertices,triangles,process=False)
    covered=np.zeros(len(triangles),bool)
    for ids in m.facets:
        ids=np.asarray(ids);ts=np.asarray(triangles)[ids]
        p0=np.asarray(vertices)[ts[0,0]];normal=m.face_normals[ids[0]]
        if np.max(np.abs((np.asarray(vertices)[np.unique(ts)]-p0)@normal))>1e-6:
            continue
        ee=np.concatenate((ts[:,[0,1]],ts[:,[1,2]],ts[:,[2,0]]))
        _,inv,cnt=np.unique(np.sort(ee,axis=1),axis=0,return_inverse=True,return_counts=True)
        bd=ee[cnt[inv]==1]
        if not len(bd) or np.any(cnt>2):continue
        starts,counts=np.unique(bd[:,0],return_counts=True)
        if np.any(counts!=1) or set(bd[:,0])!=set(bd[:,1]):continue
        nxt={int(a):int(b) for a,b in bd};loops=[];ok=True
        while nxt:
            start=next(iter(nxt));loop=[start];cur=start
            while True:
                if cur not in nxt:ok=False;break
                cur=nxt.pop(cur)
                if cur==start:break
                loop.append(cur)
                if len(loop)>len(bd):ok=False;break
            if not ok:break
            if len(loop)<3:ok=False;break
            loops.append(loop)
        if not ok:continue
        areas=[]
        for loop in loops:
            ps=np.asarray(vertices)[loop];areas.append(float(np.sum(np.cross(ps,np.roll(ps,-1,axis=0)),axis=0)@normal)/2)
        order=np.argsort(-np.abs(areas));loops=[loops[i] for i in order];areas=[areas[i] for i in order]
        if areas[0]<=0 or any(a>=0 for a in areas[1:]):continue
        covered[ids]=True
        yield loops,normal
    for i in np.where(~covered)[0]:
        if m.area_faces[i]<=1e-12:raise ValueError('Zero-area input face')
        yield [list(map(int,triangles[i]))],m.face_normals[i]

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
    normals={};planes={};report=[]
    for name,verts,faces in parts:
        name=name.replace("'",'');verts=np.asarray(verts);faces=np.asarray(faces)
        groups=list(face_groups(verts,faces)); used=sorted(set(i for loops,n in groups for loop in loops for i in loop))
        vs={i:S.add("CARTESIAN_POINT('',("+','.join(f'{float(v):.9f}'.rstrip('0') for v in verts[i])+'))') for i in used}
        fs=[]
        for loops,n in groups:
            bds=[]
            for i,loop in enumerate(loops):
                lp=S.add(f"POLY_LOOP('',{seq(vs[int(x)] for x in loop)})")
                typ='FACE_OUTER_BOUND' if i==0 else 'FACE_BOUND'
                bds.append(S.add(f"{typ}('',{ref(lp)},.T.)"))
            p0=verts[loops[0][0]];nk=tuple(np.round(n,10));pk=(*nk,round(float(np.dot(n,p0)),8))
            if pk not in planes:
                if nk not in normals:normals[nk]=S.add("DIRECTION('',("+','.join(f'{float(v):.10f}'.rstrip('0') for v in n)+'))')
                ax=S.add(f"AXIS2_PLACEMENT_3D('',{ref(vs[int(loops[0][0])])},{ref(normals[nk])},$)")
                planes[pk]=S.add(f"PLANE('',{ref(ax)})")
            fs.append(S.add(f"FACE_SURFACE('',{seq(bds)},{ref(planes[pk])},.T.)"))
        shell=S.add(f"CLOSED_SHELL('{name}',{seq(fs)})")
        brep=S.add(f"FACETED_BREP('{name}',{ref(shell)})")
        rep=S.add(f"FACETED_BREP_SHAPE_REPRESENTATION('{name}',({ref(brep)}),{ref(ctx)})")
        p=S.add(f"PRODUCT('{name}','{name}','',({ref(pc)}))");pf=S.add(f"PRODUCT_DEFINITION_FORMATION('','',{ref(p)})")
        pd=S.add(f"PRODUCT_DEFINITION('design','',{ref(pf)},{ref(dc)})");ps=S.add(f"PRODUCT_DEFINITION_SHAPE('','',{ref(pd)})")
        S.add(f"SHAPE_DEFINITION_REPRESENTATION({ref(ps)},{ref(rep)})");S.add(f"PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({ref(p)}))")
        report.append({'part':name,'input_triangles':len(faces),'planar_faces':len(fs),'vertices_used':len(vs),'hole_loops':sum(len(ls)-1 for ls,_ in groups)})
        print(report[-1],flush=True)
    S.write(path);return report

