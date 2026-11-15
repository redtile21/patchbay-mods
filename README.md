# Patchbay mods for Bitwig Studio

Mods for [Patchbay](https://github.com/shaboogen-dev/Patchbay) (BML). Both are built against Bitwig Studio 6.1.7 on macOS.

| Mod | What it does | Release |
|---|---|---|
| [save-new-version](save-new-version) | A **Save New Version** action that saves the project as the next `.bwproject` file (`name-2`, `name-3` ... or `name-ddMMyyHHmm`) and continues under it. | `save-new-version/releases/` |
| [default-tracks](default-tracks) | **New Default Instrument Track** and **New Default Audio Track** actions that create a track after the selected one (inside its group, inheriting its color) and load your Chain preset into it, plus **Bounce to Default Audio Track** in the clip right-click menus. | `default-tracks/releases/` |

To install a release, add the zip in Patchbay under Mods > Add Mod... (do not unpack it). Each mod has its own README.

To build from source: `./build.sh` inside a mod's folder (needs a JDK, a Patchbay folder and Bitwig Studio 6.1.7).
