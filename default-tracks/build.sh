#!/bin/sh
# Builds the mod into ./out/default-tracks (macOS). Needs: JDK 25, Patchbay folder, Bitwig Studio 6.1.7.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
JDK=${JAVA_HOME:-$HOME/.local/jdk/jdk-25.0.5+8/Contents/Home}
PB=${PATCHBAY:-$HOME/Desktop/Bitwig Patchbay}
BW="/Applications/Bitwig Studio.app/Contents/Java"
KIT="$PB/modkit"
WORK="$HERE/build"; OUT="$HERE/out/default-tracks"
COMPILE="$HERE/build-cache/bitwig-compile.jar"
rm -rf "$WORK" "$OUT"; mkdir -p "$WORK/classes" "$OUT" "$HERE/build-cache"
[ -f "$COMPILE" ] || "$JDK/bin/java" -jar "$KIT/bml-modkit.jar" compile-jar "$BW/bitwig.jar" "$COMPILE"
FW="$PB/mods/preferences-composition-framework/helper.jar"; FW2="$PB/mods/action-menu-composition-framework/helper.jar"; FW3="$PB/mods/notifications-framework/helper.jar"
CP="$COMPILE:$BW/libs.jar:$KIT/bml-api.jar:$FW:$FW2:$FW3"
(cd "$HERE/src" && "$JDK/bin/javac" --release 21 -proc:none -encoding UTF-8 -implicit:none -sourcepath . -cp "$CP" -d "$WORK/classes" $(find . -name '*.java'))
"$JDK/bin/java" -jar "$KIT/bml-modkit.jar" finish "$WORK/classes" "$WORK/hooks.json" "$BW/bitwig.jar" "$BW/libs.jar" "$FW" "$FW2" "$FW3"
"$JDK/bin/jar" --create --file "$OUT/helper.jar" -C "$WORK/classes" .
python3 "$HERE/finish_manifest.py" "$HERE/mod.json" "$WORK/hooks.json" "$OUT/mod.json"
cp "$HERE/README.md" "$OUT/"; cp "$HERE"/package/* "$OUT/"
echo BUILD_OK "$OUT"
