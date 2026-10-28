"""Remove zero-area facets by exact coincident welding or edge refinement.
Not a global vertex merge: coincident surfaces keep distinct topology.
"""
import numpy as np
import trimesh

def clean_degenerate(v,f,area_tol=1e-12):
 v=np.asarray(v,np.float64);f=np.asarray(f,np.int64).copy();removed=0;splits=0;welds=0
 for iteration in range(3000):
  ar=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)
  bad=np.nonzero(ar<area_tol)[0]
  if not len(bad):break
  if iteration%100==0 and len(bad)>20:print('degenerates',iteration,len(bad),flush=True)
  idx=int(bad[0]);tri=f[idx].copy();coords=v[tri]
  ds=np.linalg.norm(coords[:,None,:]-coords[None,:,:],axis=2);np.fill_diagonal(ds,np.inf)
  if np.min(ds)<1e-9:
   ia,ib=np.unravel_index(ds.argmin(),ds.shape);a,b=int(tri[ia]),int(tri[ib])
   f[f==b]=a;f=f[np.array([len(set(t))==3 for t in f])];welds+=1
  else:
   # Longest side endpoints, opposite point on that edge.
   ds=np.linalg.norm(coords[:,None,:]-coords[None,:,:],axis=2)
   ia,ib=np.unravel_index(ds.argmax(),ds.shape);ic=3-ia-ib
   a,b,c=map(int,(tri[ia],tri[ib],tri[ic]))
   hit=np.nonzero(np.any(f==a,axis=1)&np.any(f==b,axis=1))[0]
   hit=[int(h) for h in hit if h!=idx]
   if len(hit)!=1:raise RuntimeError('Cannot refine degenerate edge: '+repr(hit))
   j=hit[0];t=f[j];new=None
   for k in range(3):
    u,w,q=map(int,(t[k],t[(k+1)%3],t[(k+2)%3]))
    if {u,w}=={a,b}:new=np.array([[u,c,q],[c,w,q]])
   assert new is not None
   f=np.concatenate([np.delete(f,[idx,j],axis=0),new]);splits+=1
  removed+=1
 else:raise RuntimeError('Degenerate mesh did not converge')
 unused=np.unique(f);mp=np.full(len(v),-1);mp[unused]=np.arange(len(unused));v=v[unused];f=mp[f]
 t=trimesh.Trimesh(v,f,process=False)
 assert t.is_watertight,'Cleanup must preserve closed topology'
 assert t.is_winding_consistent
 return v,f,{'degenerate_operations':removed,'exact_welds':welds,'collinear_edge_refinements':splits,'watertight':True}
