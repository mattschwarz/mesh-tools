# Agent instructions for mesh-tools

Purpose: edit Bambu Studio `.3mf` projects (single object, multi-colour paint) without losing the
per-triangle `paint_color` data, then slice headlessly to report time and filament.

## Workflow
1. `uv run tools/inspect3mf.py <in.3mf>` first. Note mesh extents (100% scale), current scale,
   process profile, support overrides and the open-edge count. Never guess settings from memory.
2. To locate a feature: `uv run tools/render3mf.py <in.3mf> views.png` then zoom with a box
   `uv run tools/render3mf.py <in.3mf> zoom.png xmin xmax ymin ymax zmin zmax`. Look at the image
   before choosing coordinates. Coordinates are mesh coordinates at 100%, not plate coordinates.
3. Cut: `uv run tools/cut_region.py <in.3mf> <out.3mf> --box xmin xmax ymin ymax zmin zmax`.
   Always write to a NEW file; never overwrite the user's project. The tool refuses if the hole is
   not a single simple loop; widen or narrow the box rather than editing the tool.
4. Verify: re-run `inspect3mf.py` on the output. The open-edge count must equal the input's, the
   face count should drop by roughly the removed region, and `painted` must equal the face count.
   Render the edited region and show the user the image.
5. Scale: `uv run tools/rescale3mf.py <in.3mf> <out.3mf> <factor>` sets an absolute scale.
6. Estimate: `tools/slice3mf.sh <file.3mf>` (macOS, needs Bambu Studio installed) prints
   `model printing time`, layer count and filament weight. Report these in a table when comparing
   variants; multi-colour prints are dominated by flushing, so layer count drives time.

## Rules
- Do not run booleans (manifold3d) on AI-generated meshes without checking `open edges` first;
  they are usually not watertight and the boolean will fail. Use `cut_region.py` instead.
- Keep the user's original file untouched. Name outputs with a suffix describing the change.
- Report what was verified, not what was intended. If a check fails, say so with the numbers.
- Slicer settings live in `Metadata/project_settings.config` (JSON) and per-object overrides in
  `Metadata/model_settings.config` (XML) inside the 3mf zip. Change only the keys you mean to.
