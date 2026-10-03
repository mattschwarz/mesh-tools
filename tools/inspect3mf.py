#!/usr/bin/env python3
"""Summarise a Bambu Studio 3mf: size, scale, process, key settings, object overrides, mesh health."""
import sys, json, re, numpy as np; sys.path.insert(0,__import__('os').path.dirname(__file__)); from lib3mf import *
files=read_project(sys.argv[1]); V,F,pc=read_mesh(files)
ext=V.max(0)-V.min(0); s=scale_factors(files)
print(f"mesh extents (100%): {ext.round(1)} mm   scale in project: {np.round(s,3)}   printed size: {(ext*s).round(1)} mm")
print(f"faces {len(F)}  verts {len(V)}  open edges {open_edges(F)}  painted {int((pc!='').sum())}")
ps=json.loads(files['Metadata/project_settings.config'])
keys=['printer_settings_id','print_settings_id','layer_height','wall_loops','sparse_infill_density','sparse_infill_pattern','enable_support','support_type','support_on_build_plate_only','support_critical_regions_only','support_threshold_angle','outer_wall_speed','brim_type','enable_prime_tower','filament_settings_id']
for k in keys: print(f"  {k} = {ps.get(k)}")
print("object overrides:")
for m in re.finditer(r'<metadata key="([^"]+)" value="([^"]*)"/>',files['Metadata/model_settings.config'].decode().split('<part')[0]): print(f"  {m.group(1)} = {m.group(2)}")
