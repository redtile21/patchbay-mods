# Channel Strip: design

Status (2026-11-23): **working in Bitwig 6.1.7 on macOS.** Five unit devices, the strip container with its face and
macro knobs, and the companion mod (unit swapping, expanded view, knob sync) are built and live-tested. Product:
**Elodea Blackstar Channel Strip**, by Elodea Blackstar. Everything here is for Bitwig Studio 6.1.7 on macOS, loaded
through Patchbay.

## 1. What it is

- **6 slots** in series. Each slot holds one **unit**: Gain, EQ, Compressor, Saturation or Limiter, or nothing (Bypass).
  Any unit in any slot, repeats allowed.
- The **strip face** (the device in the chain) shows, per slot: a unit dropdown, a signal-flow box, and three **macro
  knobs** for the unit's three most useful parameters, with their live values drawn under them. Left and right are an
  **input meter** and an **output meter** (peak bars, peak-hold number, short-term LUFS on the output), then an **Out**
  gain knob and a **View** button.
- The **expanded view** (View button) is a window showing the real panel of every loaded unit, one row per slot with a
  "Slot N" header. It follows the dropdowns, remembers its place and size, and closes if the strip is deleted.
- **Native parameter names:** each unit is a real device, so automation and modulation show `EB Compressor > Threshold`.
- **Units do not remember settings** when swapped out; a new unit starts at its defaults.
- Version 1 is about working, not character. Non-goals: sidechain, mid/side per unit, gate, hardware emulation.

## 2. Architecture

### 2.1 Why a container plus units

Putting every unit's named parameters into every slot of one device would mean about 270 parameters (about ten Nitro
cores, each limited to 30 inports) and automation that stays in the slot when a unit moves. Instead:

```
EB BlackStrip (container .bwdevice)
  In ▶ meter ▶ [slot 1 chain] ▶ tap ▶ [slot 2 chain] ▶ tap ▶ … ▶ [slot 6] ▶ tap ▶ Out gain ▶ meter ▶ Out
                  │
                  └─ one unit device, e.g. "EB Compressor" (inserted by the companion mod)
```

- Six `nested_device_chain_slot`s in series (identifiers `SLOTn_CHAIN`), each preceded by a delay-compensation
  placeholder so the strip reports latency correctly.
- A **tap** (Nitro, `tap.nitro`) after each slot passes audio through and reports input level, output level, gain
  reduction and the unit kind, plus the three macro knob values, to that slot's drawing.
- The dropdown `SLOTn_TYPE` (Bypass, Gain, EQ, Compressor, Saturation, Limiter) chooses the unit. The strip itself
  cannot insert devices; the **companion mod** does (§2.3).
- The container device keeps UUID `4f1e9a37…`/`5d0c6a52…` (see `STRIP_UUIDS` in the mod). Both containers
  (EB BlackStrip and the TDR-style EB BlackStrip TDR) are recognised by the mod.

### 2.2 Devices

| Folder | Device | Notes |
|---|---|---|
| `devices/blackstrip/` | EB BlackStrip (container) | sources mirrored from the blueprint checkout (`devices/eb-strip`), see §4 |
| `devices/blackstrip-tdr/` | EB BlackStrip TDR (container) | same device and mod behaviour, flat charcoal look with a shader backdrop and framed sections (blueprint `devices/eb-strip-tdr`); own UUID |
| `devices/unit-gain/` | EB Gain | gain, pan, width, polarity, mono |
| `devices/unit-eq/` | EB EQ | native spectrum (output boosted +34 dB by the `tap` outport so it fills the display), band lines and points, shader response curve |
| `devices/unit-compressor/` | EB Compressor | transfer-curve shader, meters |
| `devices/unit-saturation/` | EB Saturation | tape, tube, soft and hard clip |
| `devices/unit-limiter/` | EB Limiter | lookahead limiter, meters |
| `devices/strip/` | older strip experiments | not used |

Shared look: `PALETTE.md` (units, strip face and meters use one palette).

### 2.3 Companion mod (`mod/`, id `eb-strip-console`)

Java mod built against Bitwig's obfuscated classes (compile jar in `mod/build-cache`). Pieces:

| File | Job |
|---|---|
| `Strip.java` | finds a strip's atoms by identifier, watches its dropdowns, swaps units, links knobs, opens the view |
| `StripHooks.java` | hooks on Bitwig setters: dropdown `lpr.MgQ(I)V`, view button `cbF.ymo(Z)V`, knob `kh` setters (`ZRB`, `wLf`, `GwM(D)`, `d_`, `e_`, `mEL`) |
| `StripView.java`, `StripViews.java` | the expanded view window (a `dvv` dialog with one `UTA` chain widget per loaded slot) |
| `StripActions.java` | actions for probing, manual insert/clear and opening the view (development aids) |
| `TrackSelection.java` | resolves the selected track for those actions |

How it works:
- **Auto-arm:** the first time a strip's dropdown, View button or macro knob is touched, the mod follows Bitwig's own
  references upward from that atom to the strip, track and project, and starts watching that strip. No action needed.
- **Swap:** when `SLOTn_TYPE` changes, the mod removes the slot's device and inserts the registered "EB <Unit>"
  (`chain.Gef(utt.byf(uuid), …)`) inside one undo step.
- **Macro knobs:** strip parameters `SLOTn_K1..3` (0 to 100) are linked to the loaded unit's parameters; moving either
  moves the other. Mapping per unit: Gain (Gain, Pan, Width), EQ (Low Pass, High Pass, Enhance = low and high shelf
  gains together, 0 to +6 dB), Compressor (Threshold, Ratio, Makeup), Saturation (Drive, Tone, Mix), Limiter (Input
  Gain, Ceiling, Release). After a swap the knobs take the unit's defaults.
- **View button:** a boolean parameter that springs back; pressing it opens the view, pressing it again closes it.
- **Safety:** while the view is open a 100 ms watchdog closes it if the strip leaves its parent chain, because a view of
  deleted chains crashes Bitwig.
- Bitwig loads mods only at startup.

### 2.4 Strip face (`devices/blackstrip/`)

Panel is 53 grid units high (the standard device height). Per slot column (19 wide): dropdown, signal-flow box
(`flow.sksl`), three macro knobs (9 x 9, no title). One drawing atom per slot feeds two panel items: the wide box and a
tall item under it carrying the knob names and live values (the shader picks the mode from the aspect ratio). The
meters (`meter.nitro`, `meter.sksl`) are tall drawings with peak bars, peak-hold dB number (3 s hold) and, on the
output, K-weighted short-term LUFS (ITU-R BS.1770 filters, about 3 s smoothing).

## 3. Units and parameters

Parameter identifiers are fixed (see each unit's `spec.py`). Ranges as built:

| Unit | Parameters (range) |
|---|---|
| Gain | Gain ±24 dB, Pan ±100, Width 0 to 200 %, Polarity, Mono |
| EQ | High-Pass and Low-Pass (log position 0 to 100; HP 0 = off, LP 100 = off), four bands (gain ±15 dB, freq, Q), Low/High shape (shelf/bell), HP/LP slope |
| Compressor | Threshold -60 to 0, Ratio 1 to 20, Attack 0.1 to 100 ms, Release 10 to 2000 ms, Makeup 0 to 24, Knee 0 to 24, Mix, Sidechain HPF, Stereo Link, Detector |
| Saturation | Drive 0 to 36 dB, Bias, Tone ±6 dB, Mix, Output -24 to +6, Type, Auto Gain, Oversampling |
| Limiter | Input Gain 0 to 24, Ceiling -12 to 0, Release 1 to 1000 ms, Lookahead 0 to 5 ms, Stereo Link |
| Strip | Output Gain ±24 dB, Expanded View, `SLOTn_TYPE`, `SLOTn_K1..3` (0 to 100) |

DSP is written from scratch from textbook designs (RBJ biquads, feed-forward log-domain compressor, tanh and polynomial
saturation, lookahead peak limiter, constant-power pan). We do not use decrypted Bitwig DSP.

## 4. Building (macOS)

The blueprint toolchain lives in a separate checkout (`~/Developer/bitwig-blueprint-work/bitwig-devices-blueprint`)
because parts of it are GPL-3.0; this repo holds only our sources and mirrors them under `devices/`.

```
cd ~/Developer/bitwig-blueprint-work/bitwig-devices-blueprint
.venv/bin/python devices/eb-strip/build.py --compiler-inputs local/host-tools/macos-arm64-bitwig-6.1.7/compiler-inputs.json
# units use their own build.py with --project-file devices/eb-xxx/bitwig-project.macos-6.1.7.json
cp devices/eb-strip/build/macos-6.1.7/*.bwdevice ~/Developer/bitwig-blueprint-work/patchbay-devices/
```

Mod: `channel-strip/mod/build.sh` (needs JDK 25 and the Patchbay folder), then copy `out/eb-strip-console` to
`~/Desktop/Bitwig Patchbay/mods/` and restart Bitwig. Check for `BUILD_OK`.

## 5. Lessons that bite

- Saved projects embed copies of devices: after a device change, delete the strip and insert it again. Bump the device
  `revision` string in `strip_document.py` on every change.
- Nitro and SkSL are only compiled when Bitwig loads the device; the offline `validate` checks syntax only. Nitro
  **inport order matters**: audio inports first, value inports last, or the atom fails with "Recursion in semantic
  analysis" and audio stops.
- Each Nitro core has at most 30 audio inports and 3 audio outports; displays read `f32<4>` vectors (two per drawing).
- Native knobs show 0 to 100 on the strip (static titles and tooltips), so real values are drawn by shader.
- Mod internals (obfuscated 6.1.7 names): indexed atom `lpr`, boolean atom `cbF`, continuous atom `xdh` (read `GwM()`,
  write `d_(D)`), chain `k3K`, device `utt`. A different Bitwig version needs these re-found (name map in the Patchbay
  `maps` folder). More detail in the project's memory notes.

## 6. Open items

- Docking the expanded view in Bitwig's detail panel (needs an anchor in a device header; not a priority).
- Container icon, presets and a release zip. The older "EB Blackstar Strip" device (first plan) can be deleted from the Patchbay device folder.
- A distinctive Elodea Blackstar / TDR-style look using Nitro and SkSL (version 2).
- Version 2 ideas: character modes (console EQ, VCA/opto/FET compression), more saturation models, curated strip presets.
- Remove the small build digit some unit displays draw in a corner before release.
