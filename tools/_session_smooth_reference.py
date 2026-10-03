import numpy as np, trimesh, xml.etree.ElementTree as ET, re, zipfile, os, triangle, scipy.sparse as sp, scipy.sparse.linalg as spl
from shapely.geometry import Polygon, Point
M='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
t=ET.parse('3mf/3D/Objects/object_1.model').getroot()
V=np.array([[float(v.get('x')),float(v.get('y')),float(v.get('z'))] for v in t.iter(M+'vertex')])
tris=list(t.iter(M+'triangle')); F=np.array([[int(f.get('v1')),int(f.get('v2')),int(f.get('v3'))] for f in tris]); pc=np.array([f.get('paint_color') for f in tris])
def open_edges(F):
    e=np.sort(np.vstack([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]),1); _,c=np.unique(e,axis=0,return_counts=True); return int((c==1).sum())
inbox=(V[:,0]>-22)&(V[:,0]<-12.5)&(V[:,1]>8.3)&(V[:,2]>-30)&(V[:,2]<-17)
kill=inbox[F].any(1); Fk=F[~kill]; pck=pc[~kill]
e=np.sort(np.vstack([Fk[:,[0,1]],Fk[:,[1,2]],Fk[:,[2,0]]]),1); ue,cnt=np.unique(e,axis=0,return_counts=True); be=ue[cnt==1]
near=(V[be[:,0],0]>-23)&(V[be[:,0],0]<-11)&(V[be[:,0],1]>5)&(V[be[:,0],2]>-31)&(V[be[:,0],2]<-16); hole=be[near]
adj={}
for a,b in hole: adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
loop=[hole[0,0]]; prev=None
while True:
    cur=loop[-1]; nxt=[x for x in adj[cur] if x!=prev][0]; prev=cur
    if nxt==loop[0]: break
    loop.append(nxt)
loop=np.array(loop); L=V[loop]; print("loop",len(loop))
# best-fit plane
o=L.mean(0); u,s,vt=np.linalg.svd(L-o); e1,e2,n=vt[0],vt[1],vt[2]
if n[1]<0: n=-n; e2=-e2
P2=np.c_[(L-o)@e1,(L-o)@e2]
# make the loop CCW in 2D for triangle
if Polygon(P2).exterior.is_ccw is False: loop=loop[::-1]; L=V[loop]; P2=P2[::-1]
h=np.median(np.linalg.norm(np.diff(L,axis=0),axis=1)); print("boundary edge len median",round(h,3))
seg=np.c_[np.arange(len(loop)),(np.arange(len(loop))+1)%len(loop)]
tr=triangle.triangulate({'vertices':P2,'segments':seg},f'pq30a{(0.6*h)**2:.5f}Y')  # constrained, quality, max area
TV=tr['vertices']; TT=tr['triangles']; print("cap verts",len(TV),"cap tris",len(TT))
assert np.allclose(TV[:len(loop)],P2)
newV=o+TV[len(loop):,0:1]*e1+TV[len(loop):,1:2]*e2
V2=np.vstack([V,newV]); idxmap=np.concatenate([loop,len(V)+np.arange(len(newV))])
cap=idxmap[TT]
cn=np.cross(V2[cap[:,1]]-V2[cap[:,0]],V2[cap[:,2]]-V2[cap[:,0]]).sum(0)
if cn@n<0: cap=cap[:,[0,2,1]]
F2=np.vstack([Fk,cap]); pc2=np.concatenate([pck,np.array(['4']*len(cap))])
oe=open_edges(F2); print("open edges after cap",oe); assert oe==16, oe
# bi-Laplacian fairing: free = cap verts + original verts within 1.6mm of loop; fixed = rest
from scipy.spatial import cKDTree
d,_=cKDTree(L).query(V2); ref=np.zeros(len(V2),bool); ref[F2.ravel()]=True; free=np.zeros(len(V2),bool); free[len(V):]=True; free[d<1.6]=True; free&=ref
patch=d<5.0; patch[len(V):]=True; patch&=ref; pid=np.where(patch)[0]; loc=-np.ones(len(V2),int); loc[pid]=np.arange(len(pid))
Fp=F2[patch[F2].all(1)]; Fl=loc[Fp]
rows=np.concatenate([Fl[:,0],Fl[:,1],Fl[:,1],Fl[:,2],Fl[:,2],Fl[:,0]]); cols=np.concatenate([Fl[:,1],Fl[:,0],Fl[:,2],Fl[:,1],Fl[:,0],Fl[:,2]])
A=sp.coo_matrix((np.ones(len(rows)),(rows,cols)),shape=(len(pid),len(pid))).tocsr(); A.data[:]=1
deg=np.maximum(np.asarray(A.sum(1)).ravel(),1); Lap=sp.diags(1/deg)@A-sp.identity(len(pid)); L2=(Lap@Lap).tocsr()
fl=free[pid]; fi=np.where(fl)[0]; ci=np.where(~fl)[0]; print("free verts",len(fi),"patch verts",len(pid))
X=V2[pid].copy(); Xf=spl.spsolve(L2[fi][:,fi].tocsc(),-L2[fi][:,ci]@X[ci]); X[fi]=Xf; V3=V2.copy(); V3[pid]=X
mv=np.linalg.norm(V3-V2,axis=1)[ref].max(); print("max vertex move",round(mv,3)); assert mv<2.0, mv
m=trimesh.Trimesh(V3,F2,process=False); print("open edges",open_edges(F2),"winding",m.is_winding_consistent,"degenerate",int((m.area_faces<1e-9).sum()))
remap=-np.ones(len(V3),int); remap[ref]=np.arange(ref.sum()); V3=V3[ref]; F2=remap[F2]; assert (F2>=0).all(); print('compacted verts',len(V3))
np.save('V3.npy',V3); np.save('F2.npy',F2); np.save('pc2.npy',pc2); np.save('patch.npy',pid)
# write into Matt's saved file
SRC=os.path.expanduser('~/Downloads/Meshy_AI_multi_color_200pct_notail.3mf'); DST=os.path.expanduser('~/Downloads/Meshy_AI_multi_color_200pct_notail_v2.3mf')
zin=zipfile.ZipFile(SRC); raw=zin.read('3D/Objects/object_1.model').decode()
head=raw[:raw.index('<vertices>')]; tail=raw[raw.index('</triangles>')+len('</triangles>'):]
vs="\n".join(f'     <vertex x="{x:.7g}" y="{y:.7g}" z="{z:.7g}"/>' for x,y,z in V3)
fs="\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}" paint_color="{p}"/>' for (a,b,c),p in zip(F2,pc2))
obj=head+"<vertices>\n"+vs+"\n    </vertices>\n    <triangles>\n"+fs+"\n    </triangles>"+tail
ET.fromstring(obj.encode())
with zipfile.ZipFile(DST,'w',zipfile.ZIP_DEFLATED) as z:
    for nme in zin.namelist():
        data=zin.read(nme)
        if nme=='3D/Objects/object_1.model': data=obj.encode()
        if nme=='Metadata/model_settings.config': data=re.sub(r'face_count="\d+"',f'face_count="{len(F2)}"',data.decode()).encode()
        z.writestr(nme,data)
print("wrote",DST,os.path.getsize(DST),"faces",len(F2))
