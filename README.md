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

The Blender MCP addon is installed with `uvx mcp-for-blender install-addon` (not vendored here).
## Limitations

- Single-object projects only: assumes `3D/Objects/object_1.model` and one build item.
- Cut regions are axis-aligned boxes in mesh coordinates; the hole must be a single simple loop.
- `render3mf.py` maps the four Bambu paint codes (`4`, `8`, `0C`, `1C`) to filament slots 1-4 only.
- `slice3mf.sh` calls the macOS Bambu Studio binary path; adjust for other platforms.
- No automated tests. Verify with `inspect3mf.py` (open-edge count should not change after a cut).
- The `triangle` dependency wraps Shewchuk's Triangle, which is free for private and research use
  but asks permission for commercial use.

Origin: built 2026-10-03 while removing the tail from a Meshy corgi and rescaling the print.
