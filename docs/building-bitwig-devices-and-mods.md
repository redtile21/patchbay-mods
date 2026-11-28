# Building native Bitwig devices and Patchbay mods: field notes

Lessons from building **EB BlackStrip**, a channel strip made of eleven native (Nitro) devices and a Patchbay mod
that drives them, with an LLM coding agent doing most of the work. Point your agent at this file next to the official
guides; it covers what those guides don't: what broke, why, and the habits that made the work go faster.

The stack:

- **[bitwig-devices-blueprint](https://github.com/polarity/bitwig-devices-blueprint)** builds `.bwdevice` files:
  Python scripts write the device document, Nitro code does the DSP, SkSL shaders draw displays. Read its
  `AGENTS.md`, `docs/BUILD.md` and `docs/AUTHORING.md` first.
- **[Patchbay (BML)](https://github.com/shaboogen-dev/Patchbay)** loads mods (Java hooks into Bitwig) and, through its
  Nitro Devices framework, your own devices. Read its SDK guide (`docs/sdk/` in a Patchbay install), especially
  `writing.md`, `mods.md` and `building.md`.
- Everything here was verified on **Bitwig Studio 6.1.7, macOS**, Patchbay loader 0.36. Bitwig's internal (obfuscated)
  class and method names in this file are 6.1.7-macOS names: they are different on every Bitwig build and platform.
  Treat them as examples of what to look for, not as names to paste.

## Rules for the agent

These are the habits that saved the most round trips. Put them in your agent's instructions.

1. **Check offline before asking the user to restart Bitwig.** Every Bitwig test costs the user a restart and a
   manual check. Before asking for one, run everything that can run without Bitwig: the device build and preflight,
   the mod build, Patchbay's preparation (`PREPARE_OK`, see [below](#check-the-mod-offline)), a rendered PNG of each
   changed shader, and a Python model of changed DSP.
2. **Bitwig loads mods only at startup.** Never read a log for a change the user hasn't restarted for. Ask first.
3. **Saved projects keep their own copy of each device.** After a rebuild, an open project still shows the old device
   until it is inserted again from the browser. When the user reports "nothing changed", ask whether they inserted a
   fresh one. Bumping the device's revision helps Bitwig notice the new file.
4. **Read the real log.** macOS: `~/Library/Logs/Bitwig/BitwigStudio.log` (Windows:
   `%LOCALAPPDATA%\Bitwig Studio\BitwigStudio.log`). Mod lines start with `[<mod-id>]`. Nitro compile errors appear
   **only** there: a device that fails to compile simply passes no audio.
5. **When a Bitwig feature doesn't work, compare with a native device that does.** Log what Bitwig sees for both, and
   diff. (F1 help: logging the help view's input for EB Compressor and for Compressor+ showed in one round trip that
   ours had no "sections" and a hidden callout side. Reading bytecode alone had missed both.)
6. **Read Bitwig's real bytecode.** Patchbay's compile jar is stubs only. Disassemble `bitwig.jar` from the Bitwig
   install with `javap -c -p -constants`. Strings (`ldc`) and enum names identify obfuscated classes quickly.
7. **Add temporary logging, then take it out.** A log line with the class name and the values involved beats guessing.
   Cap it (`if (n++ < 40)`), and remove it before committing.
8. **Ask the user for specific tests.** "Insert a fresh EB Compressor, select it, press F1, then do the same on
   Compressor+" gets an answer you can use; "test it" doesn't. Ask for a screenshot when the result is visual.
9. **Keep a running notes file of gotchas** (like this one) and read it at the start of every session.
10. **Never edit Bitwig's install, never ship Bitwig's files, never try to decrypt native device files.**

## Device documents (`.bwdevice`)

A device is a serialized object graph: objects with a class ID and typed fields named `name#id`. The blueprint's
Python helpers write it as JSON; `bwmodule-parser to-json file.bwdevice` (built in the blueprint's
`tools/document_codec`) turns a built file back into JSON. Use that to check what you actually built.

**Structure**

- An `ObjectRef` must point to an object serialized **earlier** in the file. A forward reference fails to load with
  "Index N out of bounds".
- An object is owned in exactly one place. Owning the same object twice (for example, an input proxy both embedded
  and listed) loads but passes no audio. Embed once, reference elsewhere.
- The first entry of the device's `panels` list is the face. Others are popups or the maximized panel.
- Keep each device's UUID and every parameter identifier stable across versions, or saved projects and presets break.
- Bump the device revision on each build you hand over. **Edit only the revision field.** A global search-and-replace
  of a value such as `Byte 3` also changed an unrelated enum field (a knob style) to an invalid value, and every device
  failed with "Unknown enum value".

**Field types to know.** In the document codec: Double, Bool, Int32, Int16 and Byte enums, String, ObjectRef. Enum
fields accept Byte or Int32. When a field's meaning is unclear, look for its enum in Bitwig's jar: the enum class's
static initializer lists the value names in order (`NONE, LEFT, RIGHT, TOP, BOTTOM`), which gives the numbers.

**Panel layout**

- Units: the panel height is fixed at 53 grid units; one grid unit is 4 interface pixels. SVG in an image panel item
  uses one SVG unit per interface pixel, whatever its width and height say: draw in 4-per-grid-unit coordinates.
- One shader drawing can feed several panel items (for example a face and a tall knob-label strip): the shader can
  tell them apart by the item's aspect ratio.
- Frames close to the edge (0.3 to 0.8 units in) look native. Large margins read as "not Bitwig".
- Panel colours are an enum: 0 red, 1 orange, 2 yellow, 3 green, 4 blue, 5 purple, 6 white, 7 black, 8 light grey,
  9 lime, 10 mint, 11 turquoise, 12 dark grey, 13 grey.
- Choosers (dropdowns) have styles: 0 button (centred text), 1 display, 2 value field, 4 flat, 5 underline,
  6 stepper, 7 plain.
- **Icon toggles** look native: a boolean parameter with a toggle button item whose icon name is a file name from
  Bitwig's `icons/device` resources (no folder), label style 1 (icon only), style 2 (borderless) and an "on" colour.
  It is grey when off.
- Panel expressions can show or hide items by parameter value, but literals must be non-negative: shift ranges
  (`GAIN+24`). Expression-bound visibility is ignored on popup panels, so popups can't change their controls by mode.

**Native features you can switch on in the document**

- **Header window icon** (the small square that opens a device's expanded view, as on Polysynth): give the device
  contents a `maximized_panel` reference to a second panel and set `is_allowed_to_show_maximized_panel`. A mod can
  hook the click to open its own window instead.
- **F1 help**: three things must all be true, or the help view shows nothing.
  1. Each control has a `help_id` (string). Bitwig looks up `<help_id>.desc` and `<help_id>.title` in its own text
     tables, which are in the app bundle. A mod can answer those lookups for your IDs.
  2. Each control has a `help_location` other than 0. 0 means "none" and hides the callout; 1 left, 2 right, 3 top,
     4 bottom. Put each control's callout on the side of the panel it sits on.
  3. The controls sit inside a "section": a group item with a non-empty help ID below the panel's root. Plain
     knobs are not help items; the help view attaches each control to its nearest section. If your controls sit
     directly in the root group, either nest them in a group or have a mod add the root as a section.
  On a device with many repeated controls (six identical slots, four identical EQ bands), describe one and say so in
  its text. Sixty callouts are unreadable.
- **Display items that work in a Patchbay device**: the native spectrum analyser item, and the scope observer
  item fed by a scope observer component (a scrolling time plot over about six seconds). In tests, the sonogram and
  the lightweight oscilloscope stayed blank.

## Nitro DSP

**Language traps**

- `tan`, `tanh`, `sinh`, `cosh`, `asin`, `acos`, `fmod` and `exp10` exist only for constant folding. On a runtime
  value they fail with "Undeclared identifier", in the log only, and the device passes no audio. Runtime built-ins
  that work: `sin cos atan exp exp2 log log2 log10 pow sqrt fabs floor ceil round trunc fmin fmax copysign`.
- Exact tanh: `e = exp(2 * clamp(x, -10, 10)); tanh = (e - 1) / (e + 1)`. For tan, use `sin / cos`.
- `range` is a reserved word. Name ports like `range_db`.
- Declare audio inports first and value inports last. The wrong order gave "Recursion in semantic analysis" at load.
- Avoid bare `{ }` blocks and reused local names in one function. Give every local a unique name.
- The blueprint's syntax validation doesn't catch semantic errors: only Bitwig's log does.

**Limits and how to live with them**

- A Nitro unit with more than three audio outputs crashed Bitwig's code generator in this setup. Keep each unit at
  three or fewer, and chain units in series when you need more.
- Send display data to a shader through those outputs. Pack several values into one sample as integer codes divided
  by 2^24 (exact in float32), for example `((a*64 + b)*64 + c)*64 + d`. The shader unpacks them.
- Booleans: `boolean_parameter` plus a toggle item plus `value_inport bool x;` works.

**Oversampling and aliasing**

- For real oversampling, use polyphase IIR half-band filters (HIIR-style allpass pairs) for 2x up and down. A
  steep design (8 coefficients, transition 0.04) is cheap and transparent. Generate the Nitro code from a script and
  check it bit for bit against a Python reference.
- Run every dry path (Mix, a Delta "what was removed" output) through a matching up/down pair, or it is out of phase
  with the wet signal by the filters' delay.
- Shortcuts that looked good and weren't: "residual" anti-aliasing tricks (averaging the curve's effect over
  in-between points, ADAA on the residual) leak an unsaturated, treble-heavy copy of the driven signal at high drive.
  A metric that counts only non-harmonic bins hides it. Textbook ADAA1 is bounded but dulls the highs. Always measure
  the **peak level** at extreme drive (36 dB into a 3 kHz tone) as well as the spectrum.
- Put a DC blocker after any asymmetric curve.

**Testing DSP**

Write a Python model of every non-trivial DSP change (NumPy is enough) and check it before building: levels at
extreme settings, frequency response, aliasing, and the dry/wet phase. A Bitwig round trip finds a wrong constant
(a shelf of +0.75 dB instead of +1.5 dB) much later than a ten-line script.

## SkSL display shaders

- A display shader reads the three audio outputs of its Nitro unit (`audioLow`, `audioMedium`, `audioHigh`) and
  nothing else. Everything it shows must come through them.
- A shader item can sit over a native display (such as the spectrum) with a transparent background (premultiplied
  alpha): that's how a response curve is drawn over a native spectrum.
- Share code between shaders by text insertion at build time (a `// @frame` marker replaced with a common file):
  one meter style, one font and one palette everywhere.
- Text is drawn with your own stroke font (letters as line segments). Check every glyph you use: a missing glyph
  silently drops a letter ("KHZ" drew as "KH").
- **Render shaders offline.** skia-python compiles SkSL: `skia.RuntimeEffect.MakeForShader(src)` plus
  `skia.RuntimeShaderBuilder`, with `uniform float3 iResolution;` prepended and test values for the inputs. Render to
  PNG and look at it before building the device.

## The mod (Java hooks)

Patchbay's mod kit compiles plain Java with annotations (`@Hook`, `@This`, `@Arg`) into hooks on Bitwig's methods.
Read Patchbay's `writing.md` for the API. Lessons:

**Finding what to hook**

- Find the setter Bitwig itself calls, and hook its return: for example, the indexed parameter's "set index" method
  for dropdowns, the boolean parameter's setter for toggles, the continuous parameter's setters for knobs. A
  document's "end of change set" was **not** called for UI edits.
- Identify objects by identifier, never by position: find a slot's chain by its `SLOTn_CHAIN` identifier and a
  dropdown by `SLOTn_TYPE`, not by walk order.
- Reflection walks over an object's fields work for finding owners (device → track → document root), with a
  visited set, both down and up.
- Look at how Bitwig does a thing before doing it yourself: deleting a device through the chain's own delete method
  removes it from the saved list. A lower-level "remove" only hid it on screen, and it came back on reload.

**Hook mechanics**

- `BEFORE_RETURN` hooks can't take primitive `@Arg` values. Read the new state from the object (`@This`) instead.
- A `BEFORE_RETURN` hook must not take an `@Arg` that javac considers dead at the method's end (not used after some
  point). Patchbay's deep verify then fails with "Bad local variable type" and **Bitwig doesn't launch**. Capture
  the argument in an `ENTRY` hook (a static field, UI thread only) and use it on return.
- `REPLACE_CALL` swaps one call inside a method: good for answering lookups (help text) while passing everything
  else through to the original.
- Private fields of Bitwig classes: reflection with `setAccessible(true)` works.
- Catch every `Throwable` in hook bodies and log it (with a cap). A hook exception lands in Bitwig's code.

**Changing the document safely**

- Wrap every document change (insert, delete, move) in a change set from the document root, and close it in
  `finally`. An exception inside an open change set leaves an undo step half-open and crashes Bitwig later.
- Never use a cached count or index as an insert position: re-read the live list. A stale index gave
  IndexOutOfBounds inside a change set, and then a crash.
- Only remove a device that is in the list you're removing it from. A missing one gives index -1 and crashed the
  audio engine.
- A value you read inside the hook of a toggle may be the **old** value. Read it at the end of the current UI event
  (Bitwig's "run at end of current event" scheduler). Reading too early flipped the 2x oversampling switch's polarity.
- Guard against feedback loops: a mod that sets knob B when knob A moves sees its own change in the hook. Use a
  "syncing" flag.
- If the mod holds a window or watcher tied to a device, check on a short timer that the device still exists, and
  close things when it doesn't. Deleting a device with the mod's window open crashed Bitwig until this was in place.

## Check the mod offline

After every mod build, run Patchbay's preparation with exactly the mods the user loads, from the Patchbay folder:

```bash
BML_MOD_SELECTION_ACTIVE=1 BML_ENABLED_MODS_FILE="$PWD/state/launch-enabled-mods.txt" \
  sh loader/prepare-mod.sh "<Bitwig's Java folder>" "$PWD/mods"
```

It must end with `PREPARE_OK`. Without the two variables it prepares every installed mod, including ones the user
has turned off, and may fail for unrelated reasons. A `DEEP_VERIFY_FAIL` here is a Bitwig that won't start.

## Design and UX that worked

- **Look native.** Use Bitwig's own widgets (knobs, choosers, toggles) and draw only displays yourself. Keep one
  palette, one meter style and one font across every device.
- **Toggles, not Off/On dropdowns**, and icon toggles where Bitwig has a fitting icon.
- **A shared frame**: every option in a titled cell, every display with captions naming its meters (IN, GR, OUT).
  Users read a family of devices faster when they all follow one layout.
- **Presets instead of a "save as default" feature.** Bitwig's presets already work. Remote control pages also live
  in presets (not in the `.bwdevice`), so ship a default preset that sets them up.
- **Small, composable devices.** Each unit works on its own; the strip is a container of units, so every unit can be
  tested alone, and units can't push one Nitro core past its limits.
- Expect some features to be session-only: a mod's memory (A/B snapshots, remembered settings) doesn't save with
  the project unless you build that. Say so in the README.

## Releasing

- A mod ships as a ZIP with its folder at the top level, including its source (`src/`, `build.json`) and checksums.
  Users add it in Patchbay with **Mods > Add Mod…** without unpacking.
- Devices ship as a plain folder that users add in Patchbay's **Device Folders**. Presets go into the user's Bitwig
  library under `Presets/<your folder>/`.
- README images must be PNG, JPEG or GIF and referenced by relative path (`images/x.png`): Patchbay's reader shows
  those and nothing from the web. Take screenshots at the size you want them shown.
- Be honest about versions. A mod written against a Bitwig build that isn't one of Patchbay's reference builds
  (6.1.3 and 6.1.4 as of loader 0.36) runs only on that exact build until it's ported to a reference build.
- **Patchbay Launcher** lists, installs and updates mods and devices straight from GitHub, but only for repositories
  laid out the way its [publishing guide](https://github.com/arius77R/patchbay-launcher/blob/main/docs/PUBLISHING.md)
  says. Read it before your first release; the traps that cost time here:
  - Each mod's manifest must be at `<mod-id>/mod.json` at the top of the repository. If a repository has any such
    folders, a released mod without one is treated as removed and hidden. A mod kept in `project/mod/` disappears.
  - The release asset is `<mod-id>-<version>.zip` (`1.2.0` or `1.2.0-dev.3`, nothing else in the name), attached to a
    published GitHub release, with `mod.id` and `mod.version` inside matching the file name.
  - `mod.name` is `Category: Name` with a category from the guide's fixed list (`Devices`, not `Device`).
  - List every framework in `requires`, including the ones you only use through `registrations` (Actions and Menus,
    Settings): the Launcher installs dependencies from `requires` alone.
  - Any manifest change is a new version; never replace a release file under the same version.
  - Devices: `.bwdevice` files on the default branch, optionally under `Bitwig-<version>/` folders (the Launcher picks
    the build for the user's Bitwig). Descriptions come from a table in the root `README.md` whose first column links
    the exact file name (`| [My Device](Bitwig-6.1.7/My%20Device.bwdevice) | Device | What it does | ... |`); previews
    from `previews/<file name, lower case, spaces as hyphens>.png`.
  - Add the repository topic `patchbay-mod` or `patchbay-devices` so it shows in the Launcher's source list.
- Icons for mod actions are 21 × 21 SVGs, black on transparent (Bitwig tints them). Draw your own; never copy
  Bitwig's.

## A session that works

1. Start by reading this file, the project's own notes and the open roadmap item.
2. Plan the change. If it touches DSP, write the Python model first; if it touches a display, render it.
3. Build the device(s) and the mod, run the preflight and `PREPARE_OK`, install.
4. Ask the user for one specific test, with what to insert fresh and what to look at.
5. On a failure: read the log, add targeted logging if the log is silent, compare with a native device.
6. When it works: remove the diagnostics, commit with a message that says why, and add any new gotcha to the notes.
