#!/usr/bin/env python3
"""Painted point renders from five sides, plus optional zoom box. usage: render3mf.py in.3mf out.png [xmin xmax ymin ymax zmin zmax]"""
import sys, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,__import__('os').path.dirname(__file__)); from lib3mf import *
files=read_project(sys.argv[1]); V,F,pc=read_mesh(files); C=V[F].mean(1)
cols=json.loads(files['Metadata/project_settings.config']).get('filament_colour',['#F99963','#000000','#E8DBB7','#D3B7A7'])
code={'4':0,'8':1,'0C':2,'1C':3}; col=np.array([cols[code[p]] if p in code and code[p]<len(cols) else '#999999' for p in pc])
if len(sys.argv)>3:
    b=[float(x) for x in sys.argv[3:9]]; m=(C[:,0]>b[0])&(C[:,0]<b[1])&(C[:,1]>b[2])&(C[:,1]<b[3])&(C[:,2]>b[4])&(C[:,2]<b[5]); C,col=C[m],col[m]
views=[('front (-Y)',0,2,1,1),('back (+Y)',0,2,1,-1),('left (-X)',1,2,0,1),('right (+X)',1,2,0,-1),('top',0,1,2,-1)]
fig,axs=plt.subplots(1,5,figsize=(30,7))
for ax,(name,a,b_,d,sgn) in zip(axs,views):
    o=np.argsort(sgn*C[:,d]); ax.scatter(C[o,a],C[o,b_],c=col[o],s=0.4,linewidths=0); ax.set_aspect('equal'); ax.set_title(name); ax.grid(True,alpha=.3)
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=70); print("wrote",sys.argv[2])
