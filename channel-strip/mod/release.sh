#!/bin/sh
# Makes the two release ZIPs in ../releases (macOS):
#   eb-strip-console-<version>.zip  the mod, with its source, for Patchbay's Add Mod
#   EB-BlackStrip-<version>.zip     the devices and presets, with the README
# The version is mod.json's. Needs what build.sh needs, plus the built devices in $DEVICES.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
STRIP=$(dirname "$HERE")
DEVICES=${DEVICES:-$HOME/Developer/bitwig-blueprint-work/patchbay-devices}
JDK=${JAVA_HOME:-$HOME/.local/jdk/jdk-25.0.5+8/Contents/Home}
VERSION=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['mod']['version'])" "$HERE/mod.json")
REL="$STRIP/releases"; STAGE="$HERE/build/release"
UNITS="Gain EQ Compressor Saturation Limiter Gate De-esser Transient Clipper"

# Every image the README shows must exist: a release never ships a broken README.
missing=0
for img in $(grep -o '](images/[^)]*)' "$HERE/README.md" | sed 's/^](//; s/)$//' | sort -u); do
  [ -f "$HERE/$img" ] || { echo "MISSING README image: $img"; missing=1; }
done
[ "$missing" = 0 ] || { echo "RELEASE_FAILED: add the images above"; exit 1; }
for d in "EB BlackStrip" "EB Visualizer"; do [ -f "$DEVICES/$d.bwdevice" ] || { echo "RELEASE_FAILED: no $DEVICES/$d.bwdevice"; exit 1; }; done
for u in $UNITS; do [ -f "$DEVICES/EB $u.bwdevice" ] || { echo "RELEASE_FAILED: no $DEVICES/EB $u.bwdevice"; exit 1; }; done

sh "$HERE/build.sh"
rm -rf "$STAGE"; mkdir -p "$STAGE" "$REL"

# The mod: the installable folder plus its source (Patchbay's mods ship their source) and checksums.
M="$STAGE/eb-strip-console"
cp -R "$HERE/out/eb-strip-console" "$M"
cp -R "$HERE/src" "$M/src"; cp "$HERE/build.json" "$M/"
(cd "$M" && find . -type f ! -name SHA256SUMS.txt | sort | sed 's|^\./||' | while read -r f; do shasum -a 256 "$f"; done > SHA256SUMS.txt)

# The devices: Devices/ for Patchbay's Device Folders, Presets/ for Bitwig's library.
D="$STAGE/EB BlackStrip"
mkdir -p "$D/Devices" "$D/Presets/EB BlackStrip" "$D/images"
cp "$DEVICES/EB BlackStrip.bwdevice" "$DEVICES/EB Visualizer.bwdevice" "$D/Devices/"
for u in $UNITS; do cp "$DEVICES/EB $u.bwdevice" "$D/Devices/"; done
cp "$STRIP"/presets/*.bwpreset "$D/Presets/EB BlackStrip/"
cp "$HERE/README.md" "$D/"
for img in $(grep -o '](images/[^)]*)' "$HERE/README.md" | sed 's/^](//; s/)$//' | sort -u); do
  cp "$HERE/$img" "$D/$img"
done
cp "$STRIP/../LICENSE" "$D/LICENSE.txt"

rm -f "$REL/eb-strip-console-$VERSION.zip" "$REL/EB-BlackStrip-$VERSION.zip"
(cd "$STAGE" && zip -q -r -X "$REL/eb-strip-console-$VERSION.zip" eb-strip-console -x '*.DS_Store')
(cd "$STAGE" && zip -q -r -X "$REL/EB-BlackStrip-$VERSION.zip" "EB BlackStrip" -x '*.DS_Store')
echo RELEASE_OK "$REL/eb-strip-console-$VERSION.zip" "$REL/EB-BlackStrip-$VERSION.zip"
