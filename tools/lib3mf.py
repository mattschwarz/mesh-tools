"""Shared helpers for Bambu Studio 3mf projects: read/write the object mesh with paint_color preserved."""
import re, zipfile, os, numpy as np, xml.etree.ElementTree as ET
M='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
OBJ='3D/Objects/object_1.model'

def read_project(path):
    z=zipfile.ZipFile(path); files={n:z.read(n) for n in z.namelist()}; z.close(); return files

def write_project(files, path):
    tmp=path+'.tmp'
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
        for n,d in files.items(): zo.writestr(n,d)
    os.replace(tmp,path)

def read_mesh(files, obj=OBJ):
    t=ET.fromstring(files[obj])
    V=np.array([[float(v.get('x')),float(v.get('y')),float(v.get('z'))] for v in t.iter(M+'vertex')])
    tris=list(t.iter(M+'triangle'))
    F=np.array([[int(f.get('v1')),int(f.get('v2')),int(f.get('v3'))] for f in tris])
    pc=np.array([f.get('paint_color') or '' for f in tris])
    return V,F,pc

def write_mesh(files, V, F, pc, obj=OBJ):
    raw=files[obj].decode(); head=raw[:raw.index('<vertices>')]; tail=raw[raw.index('</triangles>')+len('</triangles>'):]
    vs="\n".join(f'     <vertex x="{x:.7g}" y="{y:.7g}" z="{z:.7g}"/>' for x,y,z in V)
    fs="\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"'+(f' paint_color="{p}"' if p else '')+'/>' for (a,b,c),p in zip(F,pc))
    s=head+"<vertices>\n"+vs+"\n    </vertices>\n    <triangles>\n"+fs+"\n    </triangles>"+tail
    ET.fromstring(s.encode()); files[obj]=s.encode()
    ms=files['Metadata/model_settings.config'].decode()
    files['Metadata/model_settings.config']=re.sub(r'face_count="\d+"',f'face_count="{len(F)}"',ms).encode()

def open_edges(F):
    e=np.sort(np.vstack([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]),1); _,c=np.unique(e,axis=0,return_counts=True); return int((c==1).sum())

def build_transform(files):
    m=files['3D/3dmodel.model'].decode(); mo=re.search(r'<item [^>]*transform="([^"]*)"',m)
    return [float(x) for x in mo.group(1).split()]

def scale_factors(files):
    v=build_transform(files); return [float(np.linalg.norm(v[i*3:i*3+3])) for i in range(3)]
