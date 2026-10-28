#!/usr/bin/env python3
"""Recover owner STEP geometry without changing PCB, scale, or screenshots.
Dependencies: cadquery-ocp, numpy, trimesh, shapely.
Validated keycap solids are separate from the open enclosure reference.
"""
from pathlib import Path
import argparse, hashlib, json, re, tempfile, zipfile
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def recover_enclosure(source, dest):
    points, loops, bounds, faces = {}, {}, {}, []
    rx = re.compile(r'#(\d+)\s*=\s*(CARTESIAN_POINT|POLY_LOOP|FACE_OUTER_BOUND|FACE_BOUND|ADVANCED_FACE)\((.*)\);')
    for line in source.open():
        m = rx.match(line)
        if not m:
            continue
        n, kind, args = int(m[1]), m[2], m[3]
        refs = [int(x) for x in re.findall(r'#(\d+)', args)]
        if kind == 'CARTESIAN_POINT':
            points[n] = tuple(map(float, args[args.rindex('(')+1:args.rindex(')')].split(',')))
        elif kind == 'POLY_LOOP':
            loops[n] = refs
        elif kind in ('FACE_OUTER_BOUND', 'FACE_BOUND'):
            assert args.endswith('.T.'), 'Unsupported reversed boundary'
            bounds[n] = (refs[0], kind == 'FACE_OUTER_BOUND')
        else:
            assert args.endswith('.T.'), 'Unsupported reversed face'
            faces.append((n, refs[:-1]))
    vertices, triangles, lookup = [], [], {}
    def vertex(p):
        key = tuple(p)
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(key)
        return lookup[key]
    def triangle(p, normal=None):
        if normal is not None and np.dot(np.cross(p[1]-p[0], p[2]-p[0]), normal) < 0:
            p = [p[0],p[2],p[1]]
        triangles.append([vertex(x) for x in p])
    for face_id, ids in faces:
        ids = sorted(ids, key=lambda b: not bounds[b][1])
        rings = [np.asarray([points[v] for v in loops[bounds[b][0]]]) for b in ids]
        if len(rings)==1 and len(rings[0])==3:
            triangle(rings[0]); continue
        origin=rings[0][0]
        normal=sum((np.cross(rings[0][k]-origin, rings[0][k+1]-origin)
                    for k in range(1,len(rings[0])-1)), np.zeros(3))
        assert np.linalg.norm(normal)>1e-10, f'Degenerate face {face_id}'
        normal/=np.linalg.norm(normal)
        u=rings[0][1]-origin; u/=np.linalg.norm(u); v=np.cross(normal,u)
        projected=[np.column_stack(((r-origin)@u,(r-origin)@v)) for r in rings]
        polygon=Polygon(projected[0],projected[1:])
        assert polygon.is_valid, f'Invalid face {face_id}'
        xy=np.vstack(projected); xyz=np.vstack(rings)
        for t in constrained_delaunay_triangles(polygon).geoms:
            pts=[]
            for p in list(t.exterior.coords)[:3]:
                distances=np.linalg.norm(xy-np.asarray(p),axis=1); i=int(np.argmin(distances))
                assert distances[i]<1e-6, 'Unexpected new triangulation vertex'
                pts.append(xyz[i])
            triangle(pts,normal)
    mesh=trimesh.Trimesh(vertices=vertices,faces=triangles,process=False)
    mesh.merge_vertices(digits_vertex=7)
    dest.parent.mkdir(parents=True,exist_ok=True)
    mesh.export(dest)
    reread=trimesh.load(dest,force='mesh',process=False)
    assert len(reread.faces)==len(mesh.faces)
    assert np.allclose(reread.bounds,mesh.bounds,atol=0.00003)
    counts=np.bincount(mesh.edges_unique_inverse)
    return {'source_sha256':sha(source),'source_planar_faces':len(faces),
        'exported_triangles':len(mesh.faces),'dimensions_mm':mesh.extents.tolist(),
        'bounds_mm':mesh.bounds.tolist(),'watertight':bool(mesh.is_watertight),
        'open_boundary_edges':int(np.count_nonzero(counts==1)),
        'nonmanifold_edges':int(np.count_nonzero(counts>2)),
        'winding_consistent':bool(mesh.is_winding_consistent),
        'coordinate_scaling':1.0,'holes_filled':False,'source_face_omissions':0,
        'output_sha256':sha(dest),
        'status':'REFERENCE ONLY: opens as a mesh, not a closed printable assembly'}


def recover_keycaps(source, step_dest, stl_dir):
    from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS, TopoDS_Compound
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SHELL,TopAbs_SOLID
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    r=STEPControl_Reader();r.ReadFile(str(source));r.TransferRoots()
    assert r.NbShapes()>0, 'Keycap source does not import'
    s=BRepBuilderAPI_Sewing(1e-6);s.Add(r.OneShape());s.Perform()
    assert s.NbFreeEdges()==0 and s.NbMultipleEdges()==0
    shells=[];e=TopExp_Explorer(s.SewedShape(),TopAbs_SHELL)
    while e.More():
        sh=TopoDS.Shell_s(e.Current());bb=Bnd_Box();BRepBndLib.Add_s(sh,bb)
        g=GProp_GProps();BRepGProp.VolumeProperties_s(BRepBuilderAPI_MakeSolid(sh).Solid(),g)
        shells.append((sh,bb.Get(),g.Mass()));e.Next()
    outer=[x for x in shells if x[2]>0]; inner=[x for x in shells if x[2]<0]
    assert len(outer)==4 and len(inner)==4, 'Source part count changed'
    outer.sort(key=lambda t: (t[1][0],t[1][1]))
    compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
    stl_dir.mkdir(parents=True,exist_ok=True);records=[]
    for i,(sh,b,_) in enumerate(outer,1):
        mk=BRepBuilderAPI_MakeSolid(sh);cavity_count=0
        for nh,nb,_ in inner:
            if all(nb[j]>=b[j]-1e-5 and nb[j+3]<=b[j+3]+1e-5 for j in range(3)):
                mk.Add(nh);cavity_count+=1
        assert cavity_count==1
        solid=mk.Solid();assert BRepCheck_Analyzer(solid).IsValid()
        builder.Add(compound,solid)
        BRepMesh_IncrementalMesh(solid,0.01,False,0.1,False).Perform()
        dst=stl_dir/f'Extended_Keycap_{i:02}.stl'
        writer=StlAPI_Writer();assert writer.Write(solid,str(dst))
        mesh=trimesh.load(dst,force='mesh',process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent
        mesh.export(dst)
        records.append({'file':dst.name,'valid_closed_solid':True,'internal_cavities':1,
                        'dimensions_mm':mesh.extents.tolist(),'bounds_mm':mesh.bounds.tolist(),
                        'triangles':len(mesh.faces),'sha256':sha(dst)})
    step_dest.parent.mkdir(parents=True,exist_ok=True)
    w=STEPControl_Writer();w.Transfer(compound,STEPControl_AsIs);w.Write(str(step_dest))
    rr=STEPControl_Reader();rr.ReadFile(str(step_dest));rr.TransferRoots()
    imported=rr.OneShape();assert BRepCheck_Analyzer(imported).IsValid()
    e=TopExp_Explorer(imported,TopAbs_SOLID);count=0
    while e.More():count+=1;e.Next()
    assert count==4
    return {'source_sha256':sha(source),'method':'sew existing faces at 0.000001 mm; preserve inner cavities',
        'source_coordinates_preserved':True,'free_edges':0,'multiple_edges':0,
        'step_reimport_valid':True,'step_reimport_solids':count,'step_sha256':sha(step_dest),
        'parts':records,'fit_status':'Geometric export repair only; switch-stem fit is not hardware-tested',
        'quantity_note':'The source contains four cap bodies. The PCB requires six caps; use two additional copies after a stem-fit test.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');args=ap.parse_args()
    root=Path(args.root).resolve();archive=root/'CAD/Original_STEP_Exports.zip'
    assert archive.exists(), 'Missing original source archive'
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        with zipfile.ZipFile(archive) as z:
            for name in ('Alarm Clock Enclosure Step.step','Keycaps.step'):
                (td/name).write_bytes(z.read(name))
        report={'keycaps':recover_keycaps(td/'Keycaps.step',root/'CAD/Recovered/Keycaps_Recovered.step',root/'Production/Case_Parts'),
                'enclosure':recover_enclosure(td/'Alarm Clock Enclosure Step.step',root/'CAD/Recovered/Enclosure_REFERENCE_ONLY.stl'),
                'complete_clock_assembly_proven':False,
                'reason':'Neither upload supplies a placed PCB/display assembly; no component positions or case splits have been invented.'}
    checks=root/'CAD/Checks';checks.mkdir(exist_ok=True,parents=True)
    (checks/'Export_Recovery.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Keycaps: 4 validated solids and 4 watertight STL exports. Enclosure: reference mesh recovered, not closed.')

if __name__=='__main__':main()
