#!/bin/sh
# Builds one mod and writes its release ZIP, as Patchbay Launcher expects (docs/PUBLISHING.md upstream):
#   <mod-dir>/releases/<mod-id>-<version>.zip, one top folder <mod-id>/ holding the built mod, its source
#   (src/, build.json) and SHA256SUMS.txt. Older ZIPs in releases/ are removed.
# Usage: sh package-mod.sh <mod-dir> [releases-dir]   (macOS; needs what the mod's build.sh needs)
set -eu
MOD=$(cd "$1" && pwd)
REL=${2:-$MOD/releases}; mkdir -p "$REL"; REL=$(cd "$REL" && pwd)
ID=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['mod']['id'])" "$MOD/mod.json")
VERSION=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['mod']['version'])" "$MOD/mod.json")
[ "$(basename "$MOD")" = "$ID" ] || { echo "PACKAGE_FAILED: folder $(basename "$MOD") is not the mod id $ID"; exit 1; }

sh "$MOD/build.sh"
STAGE="$MOD/build/package"; rm -rf "$STAGE"; mkdir -p "$STAGE" "$REL"
cp -R "$MOD/out/$ID" "$STAGE/$ID"
cp -R "$MOD/src" "$STAGE/$ID/src"; cp "$MOD/build.json" "$STAGE/$ID/"
(cd "$STAGE/$ID" && find . -type f ! -name SHA256SUMS.txt | sort | sed 's|^\./||' | while read -r f; do shasum -a 256 "$f"; done > SHA256SUMS.txt)

# The packaged manifest's mod section must match <mod-id>/mod.json in the repository.
python3 - "$MOD/mod.json" "$STAGE/$ID/mod.json" <<'EOF'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:])
for k in ("mod", "built_against", "requires"):
    if a.get(k) != b.get(k): sys.exit(f"PACKAGE_FAILED: {k} differs between the repository and the packaged mod.json")
EOF

rm -f "$REL/$ID"-*.zip
(cd "$STAGE" && zip -q -r -X "$REL/$ID-$VERSION.zip" "$ID" -x '*.DS_Store')
echo PACKAGE_OK "$REL/$ID-$VERSION.zip"
