"""Make a printable solid from touching sculptural shells using 1.0mm voxel grid.
Only the decorative sculpture is remeshed. Functional mounts are added afterward.
"""
from pathlib import Path
import numpy as np,trimesh,manifold3d as md,vtk,time,json
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from scipy.ndimage import binary_closing,binary_opening
from skimage.measure import marching_cubes
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'Build/Compact';d=np.load(W/'shrine_topology_preserved.npz')
v=d['vertices'].astype(np.float64);f=d['faces'].astype(np.int64)
p=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(v,deep=True));p.SetPoints(pts);cells=vtk.vtkCellArray();cells.ImportLegacyFormat(numpy_to_vtkIdTypeArray(np.column_stack([np.full(len(f),3),f]).astype(np.int64).ravel(),deep=True));p.SetPolys(cells)
pitch=1.0;lo=np.floor(v.min(axis=0)/pitch)*pitch-2*pitch;hi=v.max(axis=0)+2*pitch;n=np.ceil((hi-lo)/pitch).astype(int)+1
print('grid',n,'cells',np.prod(n),flush=True)
im=vtk.vtkImageData();im.SetSpacing(pitch,pitch,pitch);im.SetOrigin(*lo);im.SetDimensions(*map(int,n));im.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1);arr=vtk_to_numpy(im.GetPointData().GetScalars());arr[:]=1
s=vtk.vtkPolyDataToImageStencil();s.SetInputData(p);s.SetOutputSpacing(pitch,pitch,pitch);s.SetOutputOrigin(*lo);s.SetOutputWholeExtent(im.GetExtent());s.Update();print('stencil',flush=True)
st=vtk.vtkImageStencil();st.SetInputData(im);st.SetStencilConnection(s.GetOutputPort());st.ReverseStencilOff();st.SetBackgroundValue(0);st.Update()
a=vtk_to_numpy(st.GetOutput().GetPointData().GetScalars()).reshape(tuple(n[::-1])).astype(bool)
print('occupied',int(a.sum()),flush=True)
a=binary_closing(a,structure=np.ones((3,3,3),bool));print('closed',int(a.sum()),flush=True)
vv,ff,_,_=marching_cubes(a.astype(np.float32),.5,spacing=(pitch,pitch,pitch),allow_degenerate=False)
# Returned axes Z,Y,X. Permutation reverses orientation; fix with trimesh.
vv=vv[:,::-1]+lo;ff=ff[:,::-1]
m=trimesh.Trimesh(vv,ff,process=False)
if m.volume<0:ff=ff[:,::-1]
print('mc',len(ff),'vol',abs(m.volume),flush=True)
a=md.Manifold(md.Mesh64(vv.astype(np.float64),ff.astype(np.uint64)));print('construct',a.status(),flush=True)
a=max(a.decompose(),key=lambda c:c.volume()).simplify(.25);print('simplified',a.num_tri(),flush=True)
from mesh_cleanup import clean_degenerate
r=a.to_mesh64();vv,ff,clean=clean_degenerate(r.vert_properties[:,:3],r.tri_verts)
m=trimesh.Trimesh(vv,ff,process=False);np.savez_compressed(W/'shrine_printable.npz',vertices=vv,faces=ff);m.export(W/'shrine_printable.stl')
mr=trimesh.load(W/'shrine_printable.stl',force='mesh',process=True);print('STL VALID',mr.is_watertight,mr.is_winding_consistent,len(mr.faces),flush=True)
(W/'ornament_remesh_report.json').write_text(json.dumps({'method':'Voxel solidification of decorative sculpture only; exact functional geometry added afterward','voxel_pitch_mm':pitch,'grid_shape':n.tolist(),'morphological_closing_grid_cells':3,'morphological_opening_grid_cells':0,'surface_simplification_tolerance_mm':.25,'boundary_edges':int((np.bincount(mr.edges_unique_inverse)==1).sum()),'nonmanifold_edges':int((np.bincount(mr.edges_unique_inverse)>2).sum()),'watertight_after_STL_reimport':bool(mr.is_watertight),'winding_consistent':bool(mr.is_winding_consistent),'triangles':len(mr.faces),'bounds_mm':mr.bounds.tolist(),'source_preserved':True,'mechanical_parts_remeshed':False,'geometry_is_modified_revision':True},indent=2)+'\n')
