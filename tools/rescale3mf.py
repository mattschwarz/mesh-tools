#!/usr/bin/env python3
"""Set an absolute scale on the single object of a Bambu 3mf. usage: rescale3mf.py in.3mf out.3mf 1.5 [x y]"""
import sys, re, numpy as np; sys.path.insert(0,__import__('os').path.dirname(__file__)); from lib3mf import *
src,dst,target=sys.argv[1],sys.argv[2],float(sys.argv[3]); xy=[float(a) for a in sys.argv[4:6]] or None
files=read_project(src); cur=scale_factors(files)[0]; k=target/cur
def rescale(mo):
    v=[float(x) for x in mo.group(2).split()]; v=[x*k for x in v[:9]]+[(xy[0] if xy else v[9]),(xy[1] if xy else v[10]),v[11]*k]
    return mo.group(1)+" ".join(repr(x) for x in v)+mo.group(3)
m,n=re.subn(r'(<item [^>]*transform=")([^"]*)(")',rescale,files['3D/3dmodel.model'].decode()); assert n==1; files['3D/3dmodel.model']=m.encode()
c,n=re.subn(r'(<assemble_item object_id="\d+" instance_id="0" transform=")([^"]*)(")',rescale,files['Metadata/model_settings.config'].decode()); assert n==1; files['Metadata/model_settings.config']=c.encode()
write_project(files,dst); print(f"{src}: scale {cur:.3f} -> {target:.3f}, wrote {dst}")
