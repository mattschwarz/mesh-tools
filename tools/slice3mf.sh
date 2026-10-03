#!/bin/zsh
# Headless slice with Bambu Studio and print the time/filament estimate. usage: slice3mf.sh in.3mf [outdir]
set -e; in="$1"; out="${2:-$(mktemp -d)}"; mkdir -p "$out"
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --slice 0 --export-3mf sliced.3mf --outputdir "$out" --debug 1 "$in" > "$out/log.txt" 2>&1
echo "== $(basename "$in")"; grep -E "^; (model printing time|total layer number|total filament weight)" "$out"/plate_*.gcode; echo "   (sliced project: $out/sliced.3mf)"
