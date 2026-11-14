# Project: Save New Version

Adds a **Save New Version** action. Run it from the Commander, or give it a shortcut in Settings > Shortcuts
(category "Save New Version"). It saves the project as the next version of its `.bwproject` file, next to
the original, and the project carries on under the new name. Bitwig's normal Save is unchanged. A project
that has never been saved gets Bitwig's normal Save As dialog.

Settings > Mods > Save New Version, **Version suffix**: `Number` gives `Song-2.bwproject`, `Song-3.bwproject` ...;
`Date and time` gives `Song-ddMMyyHHmm.bwproject`, for example `Song-1411260633.bwproject`.

## Requirements

- Patchbay with Bitwig Studio 6.1.7 on macOS (the mod is written against that build's names).
- Frameworks: Actions and Menus, and Settings (ticked automatically with the mod).
- After loading, give the action a shortcut in Settings > Shortcuts, category "Save New Version". Avoid keys
  Bitwig already uses for saving.
