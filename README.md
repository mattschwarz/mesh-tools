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
## Using this repo with AI coding tools

The tools are small CLIs with no interactive prompts, so an agent can drive the whole loop:
inspect a project, render it to find coordinates, cut or rescale, slice headlessly, and read
back the time and filament estimate. `AGENTS.md` (also loaded as `CLAUDE.md`) tells the agent
how the tools fit together and what to verify after each step.

**Claude Code**

    git clone https://github.com/mattschwarz/mesh-tools && cd mesh-tools && uv sync
    claude

Then describe the job in plain language, for example: "remove the tail from the dog in
~/Downloads/model.3mf, scale the result to 150% and tell me the print time". Claude reads
`CLAUDE.md`, runs the tools with `uv run`, and shows you the renders it used to pick the cut box.
Optional companions: the Meshy MCP server (`npx -y @meshy-ai/meshy-mcp-server`) for generating
models, and MCP-for-Blender (`uvx mcp-for-blender`) when an edit needs sculpting rather than a cut.

**Codex, Cursor, Windsurf, Gemini CLI and others**

Open the repo as the workspace. Tools that read `AGENTS.md` pick up the same instructions
automatically; for the rest, paste the contents of `AGENTS.md` into the system or rules file.
Everything else is plain Python invoked through `uv run`, so no tool-specific integration is needed.

**Good prompts to start from**

- "Inspect `<file>.3mf` and tell me the printed size, scale, process profile and support settings."
- "Render `<file>.3mf` and give me the mesh-coordinate box around the <feature>."
- "Cut that box, show me the rear view, and confirm the open-edge count did not change."
- "Write a 150% copy and slice both versions so I can compare time and filament."

## Limitations

- Single-object projects only: assumes `3D/Objects/object_1.model` and one build item.
- Cut regions are axis-aligned boxes in mesh coordinates; the hole must be a single simple loop.
- `render3mf.py` maps the four Bambu paint codes (`4`, `8`, `0C`, `1C`) to filament slots 1-4 only.
- `slice3mf.sh` calls the macOS Bambu Studio binary path; adjust for other platforms.
- No automated tests. Verify with `inspect3mf.py` (open-edge count should not change after a cut).
- The `triangle` dependency wraps Shewchuk's Triangle, which is free for private and research use
  but asks permission for commercial use.

Origin: built 2026-10-03 while removing the tail from a Meshy corgi and rescaling the print.
