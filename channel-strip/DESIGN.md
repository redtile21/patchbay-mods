# Channel Strip: design

Status: **plan only, nothing built.** This document describes a channel strip device for Bitwig Studio 6.1.7
loaded through Patchbay, the risks that could change the design, and the order of work. Sections marked
**(unverified)** are assumptions that the Phase 0 spikes must confirm or replace.

## 1. Goal

One device, modeled on classic console channel strips, that holds **6 slots** in series. Each slot holds one
**unit**: Gain, EQ, Compressor, Saturation/Clip or Limiter (or nothing). Any unit can go in any slot, so the
order of processing is up to the user. Each slot shows a few **quick controls** on the device itself; an
**expanded view** gives full control of every unit.

Non-goals for the first version: sidechain input from another track, mid/side processing per unit, a gate,
emulation of specific commercial hardware.

## 2. What we know about the platform

| Source | What it tells us |
|---|---|
| [polarity/bitwig-devices](https://github.com/polarity/bitwig-devices) | Third-party native devices (including an OTT-style compressor and a 4-band multiband FX) work in Bitwig 6.1.x via Patchbay. They ship as `.bwdevice` files. |
| [polarity/bitwig-devices-blueprint](https://github.com/polarity/bitwig-devices-blueprint) (`AGENTS.md`, `docs/BUILD.md`, `docs/AUTHORING.md`, `docs/BITWIG-TEST.md`) | How to build one: DSP in **Nitro** (`.nitro`), panel displays in **SkSL** (`.sksl`), document and panel assembled by a Python builder, compiled with the compiler JARs from your own Bitwig install. Needs Python 3.12, Rust 1.85+, JDK 17+. Offline preflight (`device_preflight.py`) gates every build. Documented targets: **Windows x64 (6.1.3, 6.1.7) and Linux x64 (6.1.7). macOS is not mentioned.** |
| Patchbay `frameworks/custom-device-registrar` ("Framework: Nitro Devices") | Registers `.bwdevice` / `.bwmodulator` / `.bwmodule` files from folders chosen under Tools > Device Folders into Bitwig's native registry by UUID; they then behave like factory devices. No API; it only loads. |
| Patchbay `frameworks/inspector-composition-framework` | A Java mod can add blocks to Bitwig's Inspector in the **Device** context, and rows to the Device block, built from Bitwig widgets (`InspectorProvider`, `blocks.block(...)`, `Rows` helpers). Controls bind to getter/setter pairs the mod supplies; **no documented way to reach the selected device's parameters.** |
| Patchbay `frameworks/panel-management-framework` | A Java mod can add a full panel ("view") to Bitwig's layout (`PanelProvider`, `panels.view(...).content(...)`). Same caveat about reaching device parameters. |
| Patchbay `frameworks/plugin-panels-framework` | Re-skins VST/CLAP plug-ins only. Not useful here. |
| [blakebratcher/bitwig-nitro-tools](https://github.com/blakebratcher/bitwig-nitro-tools) | Documents the Nitro AST (types `f32`/`f64`/ints/vectors/structs, audio/value/event ports, `init`/`process`/`reset` blocks, `if`/`switch`/loops, annotations such as `@min`/`@max`). Useful background on the language. **We do not use its decryption or key-extraction tools, and we do not copy decompiled Bitwig DSP**; all DSP in this device is written from scratch. |
| This repo (`default-tracks`, `save-new-version`) | How we already build Java mods against Bitwig 6.1.7 on macOS: `mod.json`, `build.json`, `build.sh`, framework registration via `.properties` descriptors, settings via `Bml.mod(...).settings()`. |

Known limits from `AUTHORING.md` that drive the design:

- Each Nitro core accepts at most **30 audio inports** and **3 audio outports**.
- The blueprint binds a knob to the DSP through an **audio-rate `f32` input**, so on that pattern every parameter
  uses one inport. Whether **value ports** avoid this cost is **(unverified)**.
- Each display reads **one `f32<4>` vector**; meters need their own envelope / peak-hold DSP.
- "Keep one Nitro core where possible": multi-core graphs can fail cold and pass a warm retest, so they must be
  tested in a fresh Bitwig process.
- Runtime arrays need explicit initialization.

## 3. Architecture

Two deliverables, built and released separately:

```
channel-strip/
  DESIGN.md                 this file
  device/                   the Nitro device (blueprint-style workspace)
    channel_strip.nitro     DSP, or one .nitro per core
    panel.sksl              meters and slot displays
    document.py             native parameters, panel layout, graph
    build.py
  companion/                optional Java mod, same layout as default-tracks/
    src/dev/local/channelstrip/...
    mod.json, build.json, build.sh, finish_manifest.py, package/*.properties
```

### 3.1 The device (`Channel Strip.bwdevice`)

- All DSP, all parameters, the compact panel and the meters.
- Loaded through Framework: Nitro Devices. It must be complete on its own: **every control in the expanded view is
  a real device parameter**, so the strip saves, recalls, automates and modulates with or without the companion
  mod.
- New, fixed UUID. Stable parameter identifiers from the first release (see §5.3).

### 3.2 The companion mod (`channel-strip-companion`)

A Java mod in the style of `default-tracks`, using frameworks this repo already uses plus Inspector (and
optionally Panel Management):

- **Expanded view** (§6.2): an Inspector block shown when a Channel Strip device is selected.
- **Actions** (Actions and Menus framework): Insert Channel Strip; Set Slot N to <unit>; Swap Slot N with
  Slot N±1; Reset Slot N; Copy / Paste Slot. Available in the Commander, as shortcuts, and in the device's
  right-click menu.
- Without the companion mod you still have every parameter through Bitwig's own parameter list, remote controls
  and automation, just without the grouped labels.

## 4. Units

Each unit uses up to **12 parameters** (P1 to P12; §5.1). P1 to P4 are the **quick controls** on the
device; the rest appear only in the expanded view. Ranges are a starting point.

### Gain
| # | Control | Range | Quick |
|---|---|---|---|
| P1 | Gain | -24 to +24 dB | yes |
| P2 | Pan | L100 to R100 | yes |
| P3 | Width | 0 to 200 % | yes |
| P4 | Polarity | Off / L / R / Both | yes |
| P5 | Mono | Off / On | |

### EQ (4 bands plus filters)
| # | Control | Range | Quick |
|---|---|---|---|
| P1 | Low gain | ±15 dB | yes |
| P2 | Low-mid gain | ±15 dB | yes |
| P3 | High-mid gain | ±15 dB | yes |
| P4 | High gain | ±15 dB | yes |
| P5 | HPF freq | Off, 20 Hz to 500 Hz | |
| P6 | Low freq / shape | 30 Hz to 450 Hz, shelf or bell | |
| P7 | Low-mid freq | 100 Hz to 2 kHz | |
| P8 | Low-mid Q | 0.4 to 4 | |
| P9 | High-mid freq | 600 Hz to 8 kHz | |
| P10 | High-mid Q | 0.4 to 4 | |
| P11 | High freq / shape | 1.5 kHz to 16 kHz, shelf or bell | |
| P12 | LPF freq | 3 kHz to 20 kHz, Off | |

Biquads with coefficients updated per block and smoothed parameters. A "Character" choice (clean or
console-style with gentle saturation) is a later addition if the budget allows.

### Compressor
| # | Control | Range | Quick |
|---|---|---|---|
| P1 | Threshold | -60 to 0 dB | yes |
| P2 | Ratio | 1:1 to 20:1, plus ∞ | yes |
| P3 | Makeup | 0 to +24 dB | yes |
| P4 | Mix | 0 to 100 % | yes |
| P5 | Attack | 0.1 to 100 ms | |
| P6 | Release | 10 to 2000 ms, Auto | |
| P7 | Knee | 0 to 24 dB | |
| P8 | Detector | Peak / RMS | |
| P9 | Sidechain HPF | Off, 20 Hz to 300 Hz | |
| P10 | Character | Clean / VCA / Opto / FET (envelope and curve variants) | |
| P11 | Stereo link | 0 to 100 % | |

### Saturation / Clip
| # | Control | Range | Quick |
|---|---|---|---|
| P1 | Drive | 0 to +36 dB | yes |
| P2 | Type | Tape / Tube / Soft clip / Hard clip | yes |
| P3 | Mix | 0 to 100 % | yes |
| P4 | Output | -24 to +6 dB | yes |
| P5 | Bias (asymmetry) | -1 to +1 | |
| P6 | Tone (post tilt) | ±6 dB | |
| P7 | Auto gain | Off / On | |
| P8 | Oversampling | 1× / 2× / 4× | |

### Limiter
| # | Control | Range | Quick |
|---|---|---|---|
| P1 | Input gain | 0 to +24 dB | yes |
| P2 | Ceiling | -12 to 0 dBFS | yes |
| P3 | Release | 1 to 1000 ms, Auto | yes |
| P4 | Lookahead | 0 to 5 ms | yes |
| P5 | Stereo link | 0 to 100 % | |
| P6 | True peak | Off / On (needs oversampling) | |

## 5. Slots and parameters

### 5.1 Generic parameter set per slot (recommended)

Giving every unit in every slot its own named parameters would need about 6 × 40 = 240 parameters, which is
far beyond the core limits. Instead each slot has a **fixed generic set**:

| Per slot | Count |
|---|---|
| Type (None / Gain / EQ / Compressor / Saturation / Limiter) | 1 |
| Bypass | 1 |
| P1 to P12 | 12 |
| **Slot total** | **14** |

The meaning of P1 to P12 depends on the slot's Type. The DSP reads them through the unit's table in §4.

Global: Input gain, Output gain, Strip bypass: **3**. Device total: 6 × 14 + 3 = **87 parameters**.

Trade-off: in Bitwig's automation lanes and generic parameter list they appear as `S3 P2`, not `Comp Ratio`.
The companion mod's expanded view shows real names. If Bitwig lets a device rename parameters at runtime
**(unverified)**, we use that instead.

When a slot's Type changes, P1 to P12 reset to that unit's defaults (handled by the companion mod; without it,
the user resets them manually or uses the unit's built-in neutral positions). Changing type is not automatable;
the Type parameter should be excluded from modulation if Nitro allows it **(unverified)**.

### 5.2 Mapping to Nitro cores

If every parameter costs one audio inport, two slots fit one core exactly:

| Core | Inports | Outports |
|---|---|---|
| Core A: input gain, slots 1 and 2 | stereo audio + 1 + 28 = 30 | stereo audio, meter vector for slot 1, meter vector for slot 2 |
| Core B: slots 3 and 4 | stereo audio + 28 = 29 | same |
| Core C: slots 5 and 6, output gain | stereo audio + 28 + 1 = 30 | same |

The cores are wired in series. This is the tightest point in the design: no spare inport in A or C. If value
ports do not count against the 30 **(unverified)**, collapse to a single core. If Strip bypass does not fit, it
becomes a host-level bypass or moves to Core B.

Whether a stereo audio input counts as one inport or two **(unverified)** decides whether this layout works.

### 5.3 Parameter identifiers

Stable from the first public build: `IN_GAIN`, `OUT_GAIN`, `BYPASS`, then `S{n}_TYPE`, `S{n}_BYP`,
`S{n}_P{k}` for n = 1 to 6, k = 1 to 12. Per the blueprint, revisions keep the UUID and identifiers; a breaking
change needs a new UUID and name.

### 5.4 Switching without clicks

- **Type change:** crossfade over about 20 ms from the old unit's output to the new unit's, with the new unit's
  state reset. Running two units for one crossfade is the CPU peak; Phase 0 measures it.
- **Bypass:** 10 to 20 ms crossfade, latency compensated where the unit has lookahead.
- **Parameters:** one-pole smoothing on all continuous parameters; EQ coefficients recomputed per block from
  smoothed values.

### 5.5 Latency

Limiter lookahead and oversampling add latency. Whether a Nitro device can report variable latency to Bitwig is
**(unverified)**. Fallback: the strip always reports a fixed latency (maximum lookahead plus maximum
oversampling filter delay) and pads unused paths, so latency never changes when slots change.

## 6. User interface

### 6.1 Compact view (the device panel)

Six columns, left to right in signal order, plus an I/O column:

```
┌────────┬────────┬────────┬────────┬────────┬────────┬──────┐
│ EQ   ▾ │ COMP ▾ │ SAT  ▾ │ —    ▾ │ GAIN ▾ │ LIM  ▾ │ IN   │
│ ○ ○    │ ○ ○    │ ○ ○    │        │ ○ ○    │ ○ ○    │  ○   │
│ ○ ○    │ ○ ○    │ ○ ○    │        │ ○ ○    │ ○ ○    │ OUT  │
│ ▮▮ GR  │ ▮▮ GR  │ ▮▮     │        │ ▮▮     │ ▮▮ GR  │  ○   │
│ [byp]  │ [byp]  │ [byp]  │ [byp]  │ [byp]  │ [byp]  │ ▮▮   │
└────────┴────────┴────────┴────────┴────────┴────────┴──────┘
```

- Type selector, 4 quick knobs (P1 to P4), level meter, gain-reduction meter for Compressor and Limiter, bypass.
- Knob labels change with Type if the panel supports reactive labels **(unverified)**; otherwise a small SkSL
  legend per column draws the names.
- Meter vector per slot: `[level L, level R, gain reduction, unit type]`, with peak-hold computed in DSP.

### 6.2 Expanded view

**Primary: an Inspector block** (companion mod, Inspector Composition Framework, Device context). Shown when a
Channel Strip is selected: one section per slot, titled with the unit, listing every parameter of that unit with
its real name, range and units, plus slot actions (Set type, Reset, Swap).

**Optional later: a full panel** (Panel Management Framework) showing all six slots side by side at full detail,
like a console view, following the selected strip.

Both depend on the companion mod being able to read and change the selected device's parameters through Bitwig's
internals. This is not documented in the frameworks; it is Phase 0 spike D.

**Fallback without that link:** an in-panel "detail" mode. A selector on the device switches the panel from the
6-column overview to one slot shown with all 12 controls. Whether a Nitro panel can switch layouts is
**(unverified)**.

## 7. DSP notes

All DSP written from scratch, following public textbook designs:

- **EQ:** RBJ cookbook biquads (shelf, peak, HP, LP), transposed direct form II, `f64` state if `f32` drifts.
- **Compressor:** feed-forward, log-domain gain computer with soft knee; peak or RMS detector; attack/release
  ballistics per character mode; sidechain HPF as a biquad on the detector path.
- **Saturation:** tanh and polynomial soft clip, asymmetric bias, hard clip; optional 2× or 4× polyphase
  oversampling with half-band filters.
- **Limiter:** lookahead peak limiter (delay line plus sliding-window maximum, smoothed gain), optional true-peak
  detection via 4× oversampled detector.
- **Gain:** gain, constant-power pan, mid/side width, polarity, mono sum.

Offline tests for each unit (in the build environment, before any Bitwig test): frequency response sweeps,
static compression curves, step responses for attack and release, THD versus drive, ceiling never exceeded on a
pathological test signal, silence in gives silence out, no NaN or denormals.

## 8. Plan

### Phase 0: spikes (go / no-go)
| Spike | Question | Pass |
|---|---|---|
| A | Can we build and load the blueprint device on a platform we can test on? | Blueprint Gain loads through Nitro Devices on your Mac, or we choose Windows/Linux for builds. |
| B | Parameter budget | A device with 87 parameters loads cold, saves, recalls and automates. Establish whether value ports avoid the 30-inport limit, how stereo counts, and whether three chained cores are reliable in a fresh process. |
| C | Slot switching | One slot switches between Gain and Saturation during playback without clicks; measure CPU. |
| D | Companion link | An Inspector block reads and changes one parameter of the selected Nitro device. |

Any failure goes back to this document before Phase 1 starts.

### Phase 1: units as plain DSP
Write and test each unit offline (§7). Order: Gain, EQ, Saturation, Compressor, Limiter.

### Phase 2: slot engine
Six slots, Type and Bypass, crossfades, fixed latency, global I/O, meter vectors.

### Phase 3: compact panel
Layout, labels, meters, at two UI scales.

### Phase 4: companion mod
Inspector expanded view, then actions (Set type, Reset, Swap, Copy/Paste, Insert Channel Strip).

### Phase 5: release
Factory presets (Clean Vocal, Drum Bus, Mix Bus, etc.), README, `BITWIG-TEST.md`-style live checklist,
zip releases like the other mods in this repo.

## 9. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| No macOS build setup for Nitro devices | Can't build where you test | Build on Windows/Linux and copy the `.bwdevice` to the Mac (the file may be platform independent **(unverified)**); or port the build scripts. |
| 30-inport limit per core | Fewer controls or more cores | Generic slot parameters (§5.1), three cores (§5.2), value ports if they help. |
| Multi-core unreliability | Device fails to load cold | Test every build in a fresh Bitwig process; fall back to fewer slots or fewer parameters per slot. |
| Companion mod can't reach device parameters | No named expanded view | In-panel detail mode (§6.2 fallback). |
| Latency reporting | Timing offsets in the mix | Fixed worst-case latency. |
| CPU from 6 slots plus oversampling | Heavy device | Oversampling only in Saturation and true-peak; skip processing for empty or bypassed slots after the crossfade. |
| Bitwig update changes internals | Device or companion breaks | Pin to 6.1.7 like the other mods; record the build target in each release. |

## 10. Open questions

1. Where will builds run: macOS (unknown support), Windows, or Linux?
2. Confirm the generic `S{n}_P{k}` parameter naming, or wait for Spike B to see whether named parameters fit.
3. Expanded view: Inspector block first (recommended), or the full console panel first?
4. Five or six slots? (Five frees one core's worth of headroom in §5.2.)
5. May the same unit appear in more than one slot? (The design allows it; nothing extra to build.)
6. Should unit "character" modes (console EQ, VCA/Opto/FET compressor) be in version 1 or later?
