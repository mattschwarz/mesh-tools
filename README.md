# mesh-tools

Pinned Python 3.12 environment plus small CLI tools for editing Bambu Studio `.3mf` projects
without losing colour painting. Run everything with `uv run`.

    uv run tools/inspect3mf.py  ~/Downloads/model.3mf
    uv run tools/rescale3mf.py  in.3mf out.3mf 1.5            # absolute scale (optionally x y plate position)
    uv run tools/cut_region.py  in.3mf out.3mf --box xmin xmax ymin ymax zmin zmax   # remove, cap, fair
    uv run tools/render3mf.py   in.3mf views.png [box]         # painted projections to find coordinates
    tools/slice3mf.sh           in.3mf                          # headless slice, prints time + filament

Coordinates for `--box` and `render3mf.py` are the raw mesh coordinates at 100% scale (see `inspect3mf.py`),
not plate coordinates. Find a feature with `render3mf.py`, zoom with a box, then cut.

Libraries: trimesh, manifold3d (booleans, needs a watertight mesh), pymeshlab (repair, remesh, smooth),
triangle (constrained triangulation), scipy/shapely. AI-generated meshes (Meshy etc.) are usually not
watertight, so repair with pymeshlab before trying a boolean.

`blender/addon.py` is the MCP-for-Blender addon (now installed via `uvx mcp-for-blender install-addon`).
Origin: built 2026-10-03 while removing the tail from a Meshy corgi and rescaling the print.
