# Tracks: Default Tracks

A Patchbay mod for Bitwig Studio. It adds two actions that create a track after the selected one (or at the end when no track is selected) and load your own Chain preset into it:

- **New Default Instrument Track** loads the Chain preset named `Default Instrument Track`
- **New Default Audio Track** loads the Chain preset named `Default Audio Track`

Each action can be given a shortcut (Settings > Shortcuts > "Default Tracks"), is in the Commander, and is in the right-click menu of a track.

## Presets

Save a Chain device as a preset with the names above. The mod looks for `<name>.bwpreset` anywhere under your user library (`~/Documents/Bitwig Studio/Library`), the shallowest match winning. To use another folder, run **Choose Default Track Preset Folder...** from the Commander (or give it a shortcut) and set Settings > Mods > Default Tracks > Preset location to Custom folder (choosing a folder switches it for you).

If a preset is missing, Bitwig shows a notification and no track is created.

## Requirements

Patchbay, Bitwig Studio 6.1.7 on macOS, and the Actions and Menus, Settings and Notifications frameworks (Patchbay ticks them with this mod).

## Not yet exposed

Hybrid tracks (preset `Default Hybrid Track`) are built into the code but have no action yet (`exposed` in `Kind.java`). Group tracks are not built yet.
