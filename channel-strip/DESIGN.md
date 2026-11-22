# Channel Strip: design

Status: **Spikes A, B and C passed, all five units work, the strip container is built and awaiting a live test (2026-11-18); Spike D and the companion mod are not started.** Product: **Elodea Blackstar Channel Strip**, by Elodea Blackstar. This document describes a channel strip for Bitwig Studio 6.1.7 on macOS,
loaded through Patchbay: the architecture, the risks that could change it, and the order of work. Anything marked
**(unverified)** is an assumption that a Phase 0 spike must confirm or replace.

## 1. Requirements

Decided:

- **6 slots** in series. Each slot holds one **unit**: Gain, EQ, Compressor, Saturation/Clip or Limiter (or nothing).
  Any unit can go in any slot, and the same unit may appear more than once.
- **Quick controls** for each unit are visible in Bitwig's device chain.
- An **expanded view** gives full control of every unit. It is a **console panel**: a Patchbay panel showing the
  selected strip's six slots side by side at full detail.
- **Native parameter names.** Every parameter appears in automation, modulation and the parameter list with a real
  name ("Compressor Threshold"), never a generic one ("S3 P2").
- **Builds run on macOS**, like the other mods in this repo.
- **Names:** every device carries the `EB` prefix and the work is credited to Elodea Blackstar (§3.5).
- **Version 1 is about working, not character.** Clean designs only; character modes come in version 2 (§12).

Non-goals for version 1: sidechain input from another track, mid/side processing per unit, a gate, emulation of
specific commercial hardware.

## 2. What we know about the platform

| Source | What it tells us |
|---|---|
| [polarity/bitwig-devices](https://github.com/polarity/bitwig-devices) | Third-party native devices work in Bitwig 6.1.x via Patchbay, shipped as `.bwdevice` files. Includes an OTT-style compressor and **Multiband FX-4, which "splits audio into four adjustable bands, each with its own device chain"**, so a third-party device can host nested device chains. |
| [polarity/bitwig-devices-blueprint](https://github.com/polarity/bitwig-devices-blueprint) (`AGENTS.md`, `docs/BUILD.md`, `docs/AUTHORING.md`, `docs/BITWIG-TEST.md`) | How to build one: DSP in **Nitro** (`.nitro`), displays in **SkSL** (`.sksl`), document and panel assembled by a Python builder, compiled with the compiler JARs from your own Bitwig install. Needs Python 3.12, Rust 1.85+, JDK 17+. Offline preflight gates every build. `AUTHORING.md` has a check profile for **containers**. Documented build targets: **Windows x64 and Linux x64 only.** |
| Patchbay `frameworks/custom-device-registrar` ("Framework: Nitro Devices") | Registers `.bwdevice` / `.bwmodulator` / `.bwmodule` files from folders chosen under Tools > Device Folders into Bitwig's native registry by UUID; they then behave like factory devices. No API. |
| Patchbay `frameworks/panel-management-framework` | A Java mod can add a panel ("view") to Bitwig's layout: `PanelProvider`, `panels.view(id, label).icon(...).content(...)`, with a bottom-bar button, a Show action and its own scale. Best with Panel: Streamlined Views; otherwise a tab in the lower panel. README says built against 6.1.4 on Windows; **6.1.7 on macOS (unverified)**. **No documented way to reach a device's parameters.** |
| Patchbay `frameworks/inspector-composition-framework` | Inspector blocks for a selected device. Not the chosen expanded view, but a possible place for slot actions. |
| [blakebratcher/bitwig-nitro-tools](https://github.com/blakebratcher/bitwig-nitro-tools) | Documents the Nitro AST (types, audio/value/event ports, `init`/`process`/`reset` blocks, `if`/`switch`/loops, annotations such as `@min`/`@max`). Background on the language only. **We do not use its decryption or key-extraction tools and do not copy decompiled Bitwig DSP**; all DSP here is written from scratch. |
| This repo (`default-tracks`, `save-new-version`) | How we already build Java mods against Bitwig 6.1.7 on macOS: `mod.json`, `build.json`, `build.sh`, framework registration through `.properties` descriptors, reaching Bitwig internals through obfuscated classes. |

Limits from `AUTHORING.md` that drive the design:

- Each Nitro core accepts at most **30 audio inports** and **3 audio outports**. The blueprint binds each knob through
  an audio-rate input, so on that pattern **one parameter costs one inport**.
- Each display reads **one `f32<4>` vector**; meters need their own envelope / peak-hold DSP.
- Multi-core graphs can fail cold and pass a warm retest; test them in a fresh Bitwig process.

## 3. Architecture

### 3.1 Why not one big device

Native names rule out the "generic knobs per slot" scheme. Putting every unit's named parameters into every slot of
one device would mean 6 slots × 42 unit parameters + slot controls ≈ **270 parameters**: about ten Nitro cores at
30 inports each, which the blueprint warns are unreliable. It also behaves badly: automation on "Slot 3 Compressor
Threshold" stays in slot 3 when the compressor is moved, and Bitwig's parameter list would show 270 entries.

### 3.2 Chosen: a strip container plus five unit devices

Each unit is **its own small native device**. The strip is a **container device with six slot chains in series**,
the same kind of structure as Multiband FX-4's band chains.

```
EB Blackstar Strip (container .bwdevice)
  Input gain ─▶ [Slot 1 chain] ─▶ [Slot 2] ─▶ … ─▶ [Slot 6] ─▶ Output gain
                    │
                    └─ holds one unit device, e.g. "EB Compressor" (.bwdevice)
```

Why this fits the requirements:

- **Native names come for free.** Each unit device declares its own named parameters ("Threshold", "Ratio" …).
  Bitwig shows them as `EB Compressor > Threshold` in automation and modulation, like any native device.
- **Parameter budget is small.** The largest unit (EQ) has 12 parameters; every device fits in **one Nitro core**.
- **Automation follows the unit.** Move a compressor from slot 3 to slot 1 and its automation moves with it, because it
  belongs to the device, not the slot.
- **Any unit in any slot** is just dropping a device into a chain. Bitwig's own drag, copy, paste and presets work.
- **Quick controls in the device chain:** each unit device's panel shows its quick controls and meter, nested inside
  the strip as Bitwig shows any container's devices.
- Each unit device is also usable on its own, outside a strip.

Costs and unknowns:

- A Nitro container with **six chains in series** is **(unverified)**. Multiband FX-4 shows nested chains in
  parallel bands. Fallback: one nested chain, with slots as positions in it and the companion mod keeping the count at 6.
- Slot chains accept any device, not only our units **(unverified whether this can be restricted)**. That is acceptable;
  the console panel shows non-EB devices as a generic slot.

### 3.3 Fallback: one device with named parameters

If containers fail Spike B, go back to a single device with all ≈270 named parameters, only if Spike C finds a way
to get parameters into Nitro without one inport each (value ports, or vector inports carrying several parameters).
Otherwise reduce the scope, for example fewer parameters per unit.

### 3.4 Deliverables (folder names)

```
channel-strip/
  DESIGN.md
  devices/                   Nitro workspace (blueprint layout)
    strip/                   Channel Strip container
    unit-gain/  unit-eq/  unit-compressor/  unit-saturation/  unit-limiter/
    shared/                  DSP shared between units (smoothing, biquads, meters)
  companion/                 Java mod, same layout as default-tracks/
    src/dev/local/channelstrip/...
    mod.json, build.json, build.sh, finish_manifest.py, package/*.properties
  build/macos/               macOS build profile and scripts (§8)
```

- **Devices**: six `.bwdevice` files, loaded through Framework: Nitro Devices. They work without the companion mod.
- **Companion mod**: the console panel (Panel Management Framework) and actions (Actions and Menus Framework).

### 3.5 Names and branding

| Item | Name |
|---|---|
| Product | Elodea Blackstar Channel Strip |
| Container device | **EB Blackstar Strip** |
| Unit devices | **EB Gain**, **EB EQ**, **EB Compressor**, **EB Saturation**, **EB Limiter** |
| Console panel (view label) | **Blackstar Console** |
| Companion mod | id `eb-channel-strip`, name "Elodea Blackstar: Channel Strip", author "Elodea Blackstar" |
| Action category | "Elodea Blackstar" |
| Device creator / vendor field | Elodea Blackstar **(unverified: where the Nitro document stores it)** |
| Nitro device ids | `elodea-blackstar.strip`, `elodea-blackstar.gain`, … (polarity uses `polarity.blueprint-gain`) |

Device names come from the `.bwdevice` filename, so the files are `EB Blackstar Strip.bwdevice`, `EB Gain.bwdevice`
and so on. The browser search keyword is the name, so typing "EB" or "Blackstar" finds them all.

## 4. Units

Each unit is its own device. Parameters marked **quick** appear on the device's own panel; all appear in the console
panel and in Bitwig's parameter list. Ranges are a starting point.

### EB Gain
| Parameter | Range | Quick |
|---|---|---|
| Gain | -24 to +24 dB | yes |
| Pan | L100 to R100 | yes |
| Width | 0 to 200 % | yes |
| Polarity | Off / L / R / Both | yes |
| Mono | Off / On | |

### EB EQ (4 bands plus filters)
| Parameter | Range | Quick |
|---|---|---|
| Low Gain | ±15 dB | yes |
| Low-Mid Gain | ±15 dB | yes |
| High-Mid Gain | ±15 dB | yes |
| High Gain | ±15 dB | yes |
| High-Pass | Off, 20 Hz to 500 Hz | |
| Low Freq / Low Shape | 30 Hz to 450 Hz; Shelf / Bell | |
| Low-Mid Freq, Low-Mid Q | 100 Hz to 2 kHz; 0.4 to 4 | |
| High-Mid Freq, High-Mid Q | 600 Hz to 8 kHz; 0.4 to 4 | |
| High Freq / High Shape | 1.5 kHz to 16 kHz; Shelf / Bell | |
| Low-Pass | 3 kHz to 20 kHz, Off | |

### EB Compressor
| Parameter | Range | Quick |
|---|---|---|
| Threshold | -60 to 0 dB | yes |
| Ratio | 1:1 to 20:1, ∞ | yes |
| Makeup | 0 to +24 dB | yes |
| Mix | 0 to 100 % | yes |
| Attack | 0.1 to 100 ms | |
| Release | 10 to 2000 ms, Auto | |
| Knee | 0 to 24 dB | |
| Detector | Peak / RMS | |
| Sidechain HPF | Off, 20 Hz to 300 Hz | |
| Stereo Link | 0 to 100 % | |

### EB Saturation
| Parameter | Range | Quick |
|---|---|---|
| Drive | 0 to +36 dB | yes |
| Type | Tape / Tube / Soft Clip / Hard Clip | yes |
| Mix | 0 to 100 % | yes |
| Output | -24 to +6 dB | yes |
| Bias | -1 to +1 | |
| Tone | ±6 dB tilt | |
| Auto Gain | Off / On | |
| Oversampling | 1× / 2× / 4× | |

### EB Limiter
| Parameter | Range | Quick |
|---|---|---|
| Input Gain | 0 to +24 dB | yes |
| Ceiling | -12 to 0 dBFS | yes |
| Release | 1 to 1000 ms, Auto | yes |
| Lookahead | 0 to 5 ms | yes |
| Stereo Link | 0 to 100 % | |
| True Peak | Off / On | |

### Channel Strip (the container)
| Parameter | Range |
|---|---|
| Input Gain | -24 to +24 dB |
| Output Gain | -24 to +24 dB |
| Slot 1 Bypass … Slot 6 Bypass | Off / On |

Parameter identifiers (for example `THRESHOLD`, `RATIO`, `SLOT3_BYPASS`) are fixed from the first public build.
Per the blueprint, revisions keep the UUID and identifiers; a breaking change needs a new UUID and name.

## 5. Behaviour

- **Bypass:** 10 to 20 ms crossfade per slot (container) and per unit.
- **Changing a slot's unit** is a device replacement in Bitwig. Whether that clicks during playback is part of
  Spike B; if it does, the container fades the slot out and back in around the change **(unverified whether the
  container can detect it)**.
- **Parameters:** one-pole smoothing on continuous parameters; EQ coefficients recomputed per block from smoothed
  values.
- **Latency:** the Limiter (lookahead) and Saturation (oversampling) add latency. Bitwig compensates nested devices
  normally; whether a Nitro device can report its own latency is **(unverified)**. Fallback: fixed latency per unit
  regardless of settings.

## 6. User interface

### 6.1 In the device chain (quick controls)

The Channel Strip container shows input and output gain and six slot bypass buttons; inside it, each unit device
shows its own small panel:

```
EB Blackstar Strip ┌ In ○  Out ○  [1][2][3][4][5][6] ┐
  ├ EB EQ          ○ Low  ○ LoMid  ○ HiMid  ○ High   ▮▮
  ├ EB Compressor  ○ Thr  ○ Ratio  ○ Makeup ○ Mix    ▮▮ GR
  ├ EB Saturation  ○ Drive ▾Type   ○ Mix    ○ Out    ▮▮
  ├ (empty)
  ├ EB Gain        ○ Gain ○ Pan    ○ Width  ▾Pol     ▮▮
  └ EB Limiter     ○ In   ○ Ceil   ○ Rel    ○ Look   ▮▮ GR
```

Each unit device's meter is an SkSL display fed by one `f32<4>` vector:
`[level L, level R, gain reduction, reserved]`, with peak-hold in DSP.

### 6.2 Console panel (expanded view)

A Panel Management view, "Channel Strip", from the companion mod. It follows the selected Channel Strip (or the
strip on the selected track):

```
┌ Blackstar Console: Lead Vox ────────────────────────────────────────────────┐
│ 1 EQ        2 COMP      3 SAT       4 —        5 GAIN      6 LIM     I/O  │
│ HPF ○       Thr  ○      Drive ○                Gain ○      In   ○    In ○ │
│ Low ○ ○     Ratio ○     Type ▾                 Pan  ○      Ceil ○        │
│ LoMid ○○○   Atk ○ Rel ○ Bias ○                 Width ○     Rel  ○    Out ○│
│ HiMid ○○○   Knee ○      Tone ○                 Pol ▾       Look ○        │
│ High ○ ○    Det ▾ Char▾ Mix ○ Out ○            Mono ▢      Link ○        │
│ LPF ○       SC HPF ○    OS ▾ AutoG ▢                       TP ▢          │
│ [byp] ▮▮    [byp] ▮▮GR  [byp] ▮▮               [byp] ▮▮    [byp]▮▮GR ▮▮  │
│ ⇄ ✕ ▾unit   ⇄ ✕ ▾unit   ⇄ ✕ ▾unit   + add      ⇄ ✕ ▾unit   ⇄ ✕ ▾unit     │
└─────────────────────────────────────────────────────────────────────────────┘
```

- One column per slot with **every** parameter of its unit, by name, in Bitwig's own widgets, so drag, double-click
  reset, undo, automation and modulation indicators behave natively.
- Per slot: bypass, swap left/right, remove, change unit (replaces the device with the chosen unit), add unit to an
  empty slot.
- Meters: levels and gain reduction per slot **(unverified: needs a way for the companion mod to read the devices'
  display outputs; otherwise version 1 has no meters in the console panel)**.
- A device in a slot that is not an EB unit shows its name and Bitwig's remote controls for it.

The whole panel depends on the companion mod reaching the selected strip's slot chains, the devices in them and their
parameters through Bitwig's internals. This is not documented in any framework; it is **Spike D**, and is the same
kind of work as `default-tracks/src/.../DefaultTracks.java`, which already walks tracks and inserts Chain devices.

### 6.3 Companion actions

Actions and Menus framework, in the Commander, as shortcuts and in the device right-click menu: Insert Channel Strip;
Set Slot N to <unit>; Swap Slot N with N±1; Remove Slot N; Show Console Panel.

## 7. DSP notes

All DSP written from scratch from public textbook designs:

- **EQ:** RBJ cookbook biquads (shelf, peak, high-pass, low-pass), transposed direct form II, `f64` state if `f32`
  drifts.
- **Compressor:** feed-forward, log-domain gain computer with soft knee; peak or RMS detector; attack/release
  ballistics (one clean design in version 1); sidechain HPF as a biquad on the detector path.
- **Saturation:** tanh and polynomial soft clip, asymmetric bias, hard clip; optional 2× or 4× polyphase
  oversampling with half-band filters.
- **Limiter:** lookahead peak limiter (delay line plus sliding-window maximum, smoothed gain), optional true-peak
  detection via a 4× oversampled detector.
- **Gain:** gain, constant-power pan, mid/side width, polarity, mono sum.

Offline tests for every unit: frequency response sweeps, static compression curves, attack/release step
responses, THD versus drive, ceiling never exceeded on worst-case signals, silence in gives silence out, no NaN or
denormals. Shared code (smoothing, biquads, meters) lives in `devices/shared/`, if Nitro supports includes
**(unverified)**; otherwise the build script inlines it.

## 8. Building on macOS

The blueprint's toolchain supports Windows x64 and Linux x64 only. What it needs, and the macOS equivalent:

| Blueprint input | macOS | Status |
|---|---|---|
| `bin/bitwig.jar`, `bin/libs.jar` | `/Applications/Bitwig Studio.app/Contents/Java/bitwig.jar` and `libs.jar` (as this repo's `build.sh` already uses) | known |
| Bitwig's bundled Java (`lib/jre/bin/java`) | `/Applications/Bitwig Studio.app/Contents/PlugIns/JavaVM-arm64.bundle/Contents/Home/bin/java` | **verified** |
| `javac` | your JDK 25 (`$HOME/.local/jdk/jdk-25.0.5+8/Contents/Home`) | known |
| Python 3.12, Rust 1.85+ | `brew install python@3.12`, `brew install rustup` then `rustup default stable` (Rust 1.100) | **verified** |
| Compiler profile | the blueprint already ships `macos-arm64-bitwig-6.1.7`; its jar hashes match this Bitwig exactly | **verified, nothing to write** |
| Project file `bitwig-project.linux-6.1.7.json` | `bitwig-project.macos-6.1.7.json`: a copy of the Linux overlay with platform `macos-arm64` and output `build/macos-6.1.7/` | **verified** |
| Nitro semantic probe (LLVM IR) | Windows-only already; Linux skips it with `NITRO026`, so macOS can too | acceptable |
| SkSL check in local Skia | `skia-python==144.0.post2` installs on macOS arm64 and compiles the shader | **verified** |

The approach, in order:

1. **Check portability first.** Nitro is compiled by Bitwig when the device loads, so a `.bwdevice` probably holds
   platform-neutral data **(unverified)**. Build the blueprint's Blueprint Gain on Linux or Windows and load it on
   your Mac. If it loads and runs, macOS builds help day-to-day work but don't block anything.
2. **Port the build to macOS.** Add the macOS profile and project file above, adapt any Windows/Linux paths in the
   blueprint's scripts, then build Blueprint Gain on your Mac and compare the result with the Linux or Windows
   build of the same version: matching preflight results and an identical or equivalent artifact.
3. Wrap it in `channel-strip/build.sh`, like the other mods' `build.sh`.

Before copying or forking the blueprint's scripts, check its licence and `docs/PROVENANCE.md`. The blueprint has no top-level
licence file. Its `tools/document_codec` and `tools/host_compiler` are **GPL-3.0-only** and `tools/nitro_ast` is MIT, so the
build tooling stays in a separate checkout and only our own sources (`.nitro`, `.sksl`, project files) live in this repo.

**Result (Spike A, 2026-11-18):** passed. On macOS arm64 with Bitwig 6.1.7, Blueprint Gain built, passed preflight
(`NITRO026`: the semantic probe is skipped off Windows, as expected) and loaded through Patchbay, passing the checks in the
blueprint's `BITWIG-TEST.md`. The macOS artifact has the same SHA-256 as the Windows 6.1.7 one
(`85127a64…`), so a `.bwdevice` is platform-neutral. Because the semantic probe is skipped, Nitro that parses can still fail
in the live engine: every device needs a live test.

I can't run macOS in this cloud container. Either you run the steps and send me the output, or you connect your Mac
to a session with Remote Control so I can run them there.

## 9. Plan

### Phase 0: spikes (go / no-go)

Progress: **A passed.** **C passed in part:** EB Gain (`devices/unit-gain/`) loads on 6.1.7 macOS, audio and the knobs work, automation shows the real parameter names and is recalled after reopening the project. The live engine accepted `exp`, `sin`, `cos` and vector construction even though the semantic probe is skipped on macOS. Findings from decoding polarity's devices (syntax only, no DSP copied): Nitro components keep state in ordinary member variables and process per sample; `EC.samplerate`, `smooth`, `bound`, `dbgain`, `exp`, `sqrt` exist; `value_inport` ports (not counted in the 30 audio inports) carry choices and toggles, so the §3.3 budget worry is smaller than stated; `mono` is a reserved word. The blueprint's gate only supports knob and choice controls, so toggles (Mono, bypass) are modelled as Off/On choice parameters, as OTT does. Width on EB Gain works as designed (it only acts on stereo content, not a centred source); Polarity and Mono work live. Still open from C: whether the new Polarity and Mono choices work live (built, untested), the modulation list check, and latency reporting. Width on EB Gain reported as having no effect (diagnostic build with a width bar in the display, untested). **B passed in part (2026-11-18):** `EB Strip Spike` (`devices/strip/`) has six `nested_device_chain_slot` chains in series between an input and an output gain stage, modelled on Multiband FX-4, which also holds a toggle (`boolean_value_atom`) template. It loads cold on 6.1.7 macOS (after fixing a forward reference: the loader resolves object references as it reads, so proxies must be owned before anything that points at them), shows six slots, automation works, and swapping devices in a slot during playback works with occasional small clicks (so the §5 fade-around-swap is still worth doing if the container can detect a swap). Not yet confirmed live: audio order through several slots, and save/reopen recall of nested devices. D not started. Width on EB Gain was reported not working (under investigation).

| Spike | Question | Pass |
|---|---|---|
| A | macOS build | Blueprint Gain builds on macOS (§8 step 2), or a Linux/Windows build loads and runs on your Mac (§8 step 1). |
| B | Container | A Nitro container with six chains in series loads cold, passes audio through nested devices, saves and recalls; swapping a device in a chain during playback is click-free or can be faded. |
| C | Unit device | One unit device (EB Gain) with named parameters, quick controls on its panel and a meter: automation and modulation show real names. |
| D | Companion link | A Panel Management view finds the selected Channel Strip, lists the devices in its slot chains, and reads and changes one of their parameters through Bitwig widgets. Also confirms the framework works on 6.1.7 macOS. |

If B fails, use the fallback in §3.3. If D fails, the console panel is dropped for version 1 and the full parameters
are reached through each unit device's own panel and Bitwig's parameter list.

### Phase 1: unit devices
Progress: EB Gain done as a spike. **EB Compressor built** (`devices/unit-compressor/`: threshold, ratio, makeup, mix, attack, release, knee, sidechain HPF, stereo link, detector; stereo link is a simplified linked/average detector, and Release Auto and Ratio infinity are deferred), preflight passes, live test: works. **EB EQ built** (`devices/unit-eq/`, generated by `gen_eq.py`: six RBJ biquads, coefficients recomputed only when a band's parameters change; frequency knobs are linear because the blueprint gate only accepts linear decimal controls, so a log mapping is an open item; Low-Pass at 20000 and High-Pass below 20 Hz are off), preflight passes, live test: works. **EB Saturation built** (`devices/unit-saturation/`: tape, tube, soft and hard clip, bias, tone tilt, auto gain, oversampling 1x/2x using a simple 2-point interpolator and averager, not a proper half-band, 4x deferred; no latency), and **EB Limiter built** (`devices/unit-limiter/`: lookahead peak limiter with window-minimum gain, one-pole release, hard safety clip at the ceiling, array state with the recall canary the blueprint gate requires; True Peak, Release Auto and PDC reporting deferred), both preflight-clean, live test: both work, so Phase 1 is done. **Phase 2 started:** `EB Blackstar Strip` (`devices/strip/`) replaces the spike: input and output gain, six chain slots in series, and a per-slot bypass (an Off/On choice parameter feeding a 15 ms crossfade core between the slot's input and output), preflight passes, live test pending. The generic unit builder (`eb-unit`, adapted from the blueprint) stays outside this repo.
Gain, EQ, Saturation, Compressor, Limiter: DSP with offline tests, then each device's panel and meter.

### Phase 2: container
Six slot chains, input and output gain, slot bypass with crossfades, latency.

### Phase 3: companion mod
Console panel, then actions.

### Phase 4: release
Factory presets for the strip (Clean Vocal, Drum Bus, Mix Bus, etc.), README, a live test checklist following
the blueprint's `BITWIG-TEST.md`, zip releases like the other mods in this repo.

## 10. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| No macOS build | Can't build where you test | §8: portability check first; port the profile. |
| Serial six-chain container not possible | No slot structure | One nested chain with positions as slots; or the single-device fallback (§3.3). |
| Companion mod can't reach slots and parameters | No console panel | Unit device panels and Bitwig's parameter list for version 1. |
| Panel Management Framework on 6.1.7 macOS | No console panel | Spike D tests it first; ask the framework's author. |
| Latency reporting | Timing offsets | Fixed latency per unit. |
| CPU with oversampling | Heavy strip | Oversampling only in Saturation and True Peak. |
| Bitwig update changes internals | Devices or companion break | Pin to 6.1.7, record the build target in each release. |

## 10b. Polish round 1 (2026-11-18)

Decoding polarity's devices showed Bitwig has native display widgets the blueprint gate does not mention: a display panel
(log frequency axis, dB axis, native spectrum analyser, lines and points driven by panel expressions on parameter
identifiers), native stereo peak meters (`vu_meter_atom` + `meter_panel_item`), and up to three shader vectors. Round 1:
- **EQ:** native spectrum of the output with lines at the band frequencies and points at (frequency, gain), plus native in
  and out meters. Points are not yet draggable and the combined response curve is not drawn (needs a polyline of points
  with computed expressions, or packed shader parameters).
- **Compressor:** transfer-curve shader (threshold, ratio, knee, makeup) with a live operating point, gain-reduction and
  mix bars, native in and out meters, knobs on the smaller native size.
- **Limiter:** input and output level bars with the ceiling line, gain-reduction bar, lookahead and release readouts, native
  meters.
- **Strip:** the slot bypass behaviour was reported inverted; the condition is flipped.
- **Swappable modules without the browser** is the companion console (Spike D) and is deliberately next, after these
  devices are refined.

## 11. Open questions

1. Is Panel: Streamlined Views installed? It decides whether the console panel is its own view or a tab in the lower panel.

## 12. Version 2: making it amazing

Deferred so version 1 can focus on working end to end:

- Character modes: console-style EQ curves; VCA, Opto and FET compressor ballistics and curves.
- Saturation models beyond the four basic curves.
- A distinctive Elodea Blackstar look for the panels and console (colours, artwork, SkSL displays).
- Meters in the console panel, if version 1 ships without them.
- Strip presets curated by Elodea Blackstar.

## 10c. Polish round 2 (2026-11-19)

Compressor and limiter follow the built-in Bitwig layout: shader-drawn input and output meters with blue threshold/ceiling lines and peak-hold ticks, held-peak numeric readouts (5 s hold, gain reduction refreshes once per second), main knobs in one row under the display. The EQ draws its combined response curve in a transparent shader over the native spectrum display, with knobs grouped by band. Display data is packed into two vectors (hybrid gate limit). Saved projects embed device copies, so re-insert devices after a rebuild. A small build digit in each display corner is a version stamp to remove before release.
