#!/usr/bin/env python3
"""Remove everything inside an axis-aligned box (mesh coordinates, 100% scale), cap the hole with a quality
triangulation and fair the cap plus a ring of surrounding surface so it blends in. Paint colours preserved.
usage: cut_region.py in.3mf out.3mf --box xmin xmax ymin ymax zmin zmax [--cap-color 4] [--fair 1.6]"""
import sys, argparse, numpy as np, trimesh, triangle, scipy.sparse as sp, scipy.sparse.linalg as spl
from scipy.spatial import cKDTree; from shapely.geometry import Polygon
sys.path.insert(0,__import__('os').path.dirname(__file__)); from lib3mf import *
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('--box',nargs=6,type=float,required=True)
ap.add_argument('--cap-color',default=None,help="paint_color code for cap faces; default = colour of the removed faces nearest the rim")
ap.add_argument('--fair',type=float,default=1.6,help='radius (mm) of surrounding surface to fair with the cap'); a=ap.parse_args()
files=read_project(a.src); V,F,pc=read_mesh(files); x0,x1,y0,y1,z0,z1=a.box
inbox=(V[:,0]>x0)&(V[:,0]<x1)&(V[:,1]>y0)&(V[:,1]<y1)&(V[:,2]>z0)&(V[:,2]<z1)
kill=inbox[F].any(1); Fk=F[~kill]; pck=pc[~kill]; oe0=open_edges(F)
print(f"removing {kill.sum()} faces; open edges before {oe0}")
e=np.sort(np.vstack([Fk[:,[0,1]],Fk[:,[1,2]],Fk[:,[2,0]]]),1); ue,cnt=np.unique(e,axis=0,return_counts=True); be=ue[cnt==1]
# boundary edges of the new hole = open edges touching a removed face's vertex
killed_v=np.zeros(len(V),bool); killed_v[F[kill].ravel()]=True; hole=be[killed_v[be].any(1)]
adj={}
for p,q in hole: adj.setdefault(p,[]).append(q); adj.setdefault(q,[]).append(p)
assert all(len(v)==2 for v in adj.values()), "hole boundary is not a single simple loop; adjust the box"
loop=[hole[0,0]]; prev=None
while True:
    cur=loop[-1]; nxt=[x for x in adj[cur] if x!=prev][0]; prev=cur
    if nxt==loop[0]: break
    loop.append(nxt)
loop=np.array(loop); L=V[loop]; o=L.mean(0); _,_,vt=np.linalg.svd(L-o); e1,e2,n=vt
P2=np.c_[(L-o)@e1,(L-o)@e2]
if not Polygon(P2).exterior.is_ccw: loop=loop[::-1]; L=L[::-1]; P2=P2[::-1]
h=np.median(np.linalg.norm(np.diff(L,axis=0),axis=1)); seg=np.c_[np.arange(len(loop)),(np.arange(len(loop))+1)%len(loop)]
tr=triangle.triangulate({'vertices':P2,'segments':seg},f'pq30a{(0.6*h)**2:.6f}Y'); TV,TT=tr['vertices'],tr['triangles']
newV=o+TV[len(loop):,0:1]*e1+TV[len(loop):,1:2]*e2; V2=np.vstack([V,newV]); idx=np.concatenate([loop,len(V)+np.arange(len(newV))]); cap=idx[TT]
# orient cap to match the kept surface: a shared edge must run in opposite directions on the two sides
kept_dir=set(map(tuple,np.vstack([Fk[:,[0,1]],Fk[:,[1,2]],Fk[:,[2,0]]])))
cap_dir=np.vstack([cap[:,[0,1]],cap[:,[1,2]],cap[:,[2,0]]]); same=sum(tuple(e) in kept_dir for e in cap_dir); opp=sum((e[1],e[0]) in kept_dir for e in cap_dir)
if same>opp: cap=cap[:,[0,2,1]]
print(f"cap orientation: {opp} edges opposed, {same} aligned -> {'flipped' if same>opp else 'kept'}")
F2=np.vstack([Fk,cap]); oe=open_edges(F2); assert oe==oe0, f"cap did not close the hole cleanly ({oe} vs {oe0})"
rimc=pc[kill][cKDTree(V[F[kill]].mean(1)).query(V2[cap].mean(1))[1]]; capc=np.array([a.cap_color]*len(cap)) if a.cap_color else rimc
pc2=np.concatenate([pck,capc])
# bi-Laplacian fairing of cap + ring
ref=np.zeros(len(V2),bool); ref[F2.ravel()]=True; d,_=cKDTree(L).query(V2)
free=np.zeros(len(V2),bool); free[len(V):]=True; free[d<a.fair]=True; free&=ref
patch=(d<a.fair+3.5)|free; patch&=ref; pid=np.where(patch)[0]; loc=-np.ones(len(V2),int); loc[pid]=np.arange(len(pid))
Fl=loc[F2[patch[F2].all(1)]]; rows=np.concatenate([Fl[:,0],Fl[:,1],Fl[:,1],Fl[:,2],Fl[:,2],Fl[:,0]]); cols=np.concatenate([Fl[:,1],Fl[:,0],Fl[:,2],Fl[:,1],Fl[:,0],Fl[:,2]])
A=sp.coo_matrix((np.ones(len(rows)),(rows,cols)),shape=(len(pid),len(pid))).tocsr(); A.data[:]=1
deg=np.maximum(np.asarray(A.sum(1)).ravel(),1); Lap=sp.diags(1/deg)@A-sp.identity(len(pid)); L2=(Lap@Lap).tocsr()
fl=free[pid]; fi=np.where(fl)[0]; ci=np.where(~fl)[0]; X=V2[pid].copy(); X[fi]=spl.spsolve(L2[fi][:,fi].tocsc(),-L2[fi][:,ci]@X[ci]); V3=V2.copy(); V3[pid]=X
mv=np.linalg.norm(V3-V2,axis=1)[ref].max(); print(f"cap {len(cap)} faces, faired {len(fi)} verts, max move {mv:.2f} mm")
remap=-np.ones(len(V3),int); remap[ref]=np.arange(ref.sum()); V3=V3[ref]; F2=remap[F2]
m=trimesh.Trimesh(V3,F2,process=False); assert m.is_winding_consistent and (m.area_faces>1e-9).all()
write_mesh(files,V3,F2,pc2); write_project(files,a.dst); print(f"wrote {a.dst}: {len(F2)} faces, open edges {open_edges(F2)}")
