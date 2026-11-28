# Patchbay mods for Bitwig Studio

Mods for [Patchbay](https://github.com/shaboogen-dev/Patchbay) (BML). All are built against Bitwig Studio 6.1.7 on macOS.

| Mod | What it does | Release |
|---|---|---|
| [save-new-version](save-new-version) | A **Save New Version** action that saves the project as the next `.bwproject` file (`name-2`, `name-3` ... or `name-ddMMyyHHmm`) and continues under it. | `save-new-version/releases/` |
| [eb-strip-console](eb-strip-console) | **EB Strip Console**, the companion mod of **EB BlackStrip**: a channel strip of native (Nitro) devices (six swappable slots, nine processing units, character, loudness and gain match, a visualizer). The devices, presets and design notes are in [channel-strip](channel-strip); the devices are also at [Patchbay-devices](https://github.com/redtile21/Patchbay-devices). | `channel-strip/releases/` |
| [default-tracks](default-tracks) | **New Default Instrument Track** and **New Default Audio Track** actions that create a track after the selected one (inside its group, inheriting its color) and load your Chain preset into it, plus **Bounce to Default Audio Track** in the clip right-click menus. | `default-tracks/releases/` |

To install a mod, add `redtile21/patchbay-mods` as a source in Patchbay Launcher (Sources → Mods), or add its zip in Patchbay under Mods > Add Mod... (do not unpack it). Each mod has its own README.

To make a release ZIP: `sh package-mod.sh <mod-folder>` (for EB Strip Console, `sh eb-strip-console/release.sh`, which also makes the devices ZIP). Then attach the ZIP to a published GitHub release.

To build from source: `./build.sh` inside a mod's folder (needs a JDK, a Patchbay folder and Bitwig Studio 6.1.7).

Building something similar? [docs/building-bitwig-devices-and-mods.md](docs/building-bitwig-devices-and-mods.md)
collects what we learned making native Bitwig devices and Patchbay mods with an LLM agent: format traps, Nitro limits,
hook mechanics and a working routine. Point your agent at it.
