#!/bin/sh
# Builds the EB devices from the sources in devices/ into built/Bitwig-6.1.7/ (macOS, Bitwig 6.1.7).
#
# The sources live here, in the project. The build tools are in a checkout of polarity/bitwig-devices-blueprint
# ($BLUEPRINT), and each device's build.py finds them relative to its own folder, so the builds run there: this script
# copies devices/eb-* and devices/common/* into the checkout's devices/ folder, builds, and writes the .bwdevice files
# back into the project. Edit the sources here, not in the checkout.
#
# Usage: sh build-devices.sh [--pull | --push] [device ...]
#   device: gain eq compressor saturation limiter gate deesser transient clipper strip visualizer (default: all)
#   If the checkout's copy differs from the project's, the script stops and lists the files:
#     --pull  takes the checkout's version into the project first (for edits made in the checkout)
#     --push  overwrites the checkout's version with the project's
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
SRC="$HERE/devices"
BP=${BLUEPRINT:-$HOME/Developer/bitwig-blueprint-work/bitwig-devices-blueprint}
BITWIG=6.1.7
OUT="$HERE/built/Bitwig-$BITWIG"
INPUTS="$BP/local/host-tools/macos-arm64-bitwig-$BITWIG/compiler-inputs.json"
PY="$BP/.venv/bin/python"

MODE=check
case "${1:-}" in --pull) MODE=pull; shift ;; --push) MODE=push; shift ;; esac
DEVICES=${*:-gain eq compressor saturation limiter gate deesser transient clipper strip visualizer}

[ -x "$PY" ] || { echo "BUILD_FAILED: no blueprint checkout with a .venv at $BP (set BLUEPRINT)"; exit 1; }
[ -f "$INPUTS" ] || { echo "BUILD_FAILED: no compiler inputs for Bitwig $BITWIG at $INPUTS"; exit 1; }

# Compare the project's sources with the checkout's and copy them across.
python3 - "$SRC" "$BP/devices" "$MODE" <<'EOF'
import filecmp, shutil, sys
from pathlib import Path
src, bp, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
SKIP = {"build", "__pycache__", ".DS_Store"}
def files(root, pattern):
    out = set()
    for top in root.glob(pattern):
        if top.is_file():
            out.add(top.relative_to(root)); continue
        for f in top.rglob("*"):
            rel = f.relative_to(root)
            if f.is_file() and not SKIP & set(rel.parts) and f.suffix not in (".pyc", ".bak"):
                out.add(rel)
    return out
ours = files(src, "eb-*") | files(src, "common/*")
# the checkout's common/ also holds the blueprint's own helpers: compare only the files the project keeps there
theirs = files(bp, "eb-*") | {Path("common") / p.name for p in (bp / "common").glob("*") if (src / "common" / p.name).is_file()}
changed = sorted(p for p in ours & theirs if not filecmp.cmp(src / p, bp / p, shallow=False))
only_theirs = sorted(theirs - ours)
only_ours = sorted(ours - theirs)
if mode == "check" and (changed or only_theirs):
    print("BUILD_STOPPED: the blueprint checkout's sources differ from the project's:")
    for p in changed: print("  changed:", p)
    for p in only_theirs: print("  only in the checkout:", p)
    print("Run with --pull to take the checkout's version into the project, or --push to overwrite it.")
    sys.exit(1)
if mode == "pull":
    for p in changed + only_theirs:
        (src / p).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(bp / p, src / p); print("  pulled", p)
    changed = []
for p in changed + only_ours:
    (bp / p).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src / p, bp / p)
if mode == "push" and only_theirs:
    print("  left in the checkout (not in the project):", *map(str, only_theirs))
print(f"SOURCES_OK {len(ours)} files")
EOF

mkdir -p "$OUT"
for d in $DEVICES; do
  case $d in
    gain) name="EB Gain" ;; eq) name="EB EQ" ;; compressor) name="EB Compressor" ;; saturation) name="EB Saturation" ;;
    limiter) name="EB Limiter" ;; gate) name="EB Gate" ;; deesser) name="EB De-esser" ;; transient) name="EB Transient" ;;
    clipper) name="EB Clipper" ;; strip) name="EB BlackStrip" ;; visualizer) name="EB Visualizer" ;;
    *) echo "BUILD_FAILED: unknown device $d"; exit 1 ;;
  esac
  dir="$BP/devices/eb-$d"
  project="$dir/bitwig-project.macos-$BITWIG.json"; [ -f "$project" ] || project="$dir/bitwig-project.json"
  (cd "$BP" && "$PY" "devices/eb-$d/build.py" --compiler-inputs "$INPUTS" --project-file "$project" --out "$OUT/$name.bwdevice") \
    > "$OUT/.build-$d.log" 2>&1 || { tail -20 "$OUT/.build-$d.log"; echo "BUILD_FAILED: $name"; exit 1; }
  rm -f "$OUT/.build-$d.log"
  echo "built $name"
done
echo BUILD_OK "$OUT"
