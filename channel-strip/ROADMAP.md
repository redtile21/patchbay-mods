# EB BlackStrip roadmap

Written 2026-11-24, after the core strip (six swappable slots, macro knobs, meters, expanded view, metal knobs) was
working. Notes on feasibility reflect the constraints of the build: Nitro cores (at most 30 inports and 3 audio
outports each), the companion mod that swaps units, and panel expressions for interface-side behaviour.

## Order of work

1. Theme consistency pass (section 1)
2. Compressor modes and limiter true-peak ceiling (section 2)
3. Presets, default settings, remember settings on swap (section 4)
4. Auto gain match (section 4)
5. Strip character switch (section 3)
6. New units (section 5), then release (section 7)

## 1. Consistency and polish

- [x] One meter style everywhere: the strip's blue → amber → red bars and light-blue numbers. Units still use their
      own colours (for example the teal-green bar on Gain). Write meter colours and number style once in a shared
      source that every shader takes.
- [ ] Shared unit frame: the same header, frames, label case and spacing on every unit.
- [x] Remove the build digit in the corner of the unit displays.
- [x] Clearer slot states on the strip: a dimmed box for a bypassed slot, a gain-reduction bar on Compressor and
      Limiter slots (already in place; the slot output bar now uses the shared ramp).

## 2. Modes inside the existing units

Each mode is a chooser inside the same unit; knobs and automation stay the same, only the maths changes.

- [x] Compressor: VCA (clean, fast, hard knee), Opto (two-stage, program-dependent release), FET (very fast attack,
      aggressive, "all buttons" option), Vari-Mu (soft knee, ratio rises with level).
- [ ] EQ: Clean (current), Console (proportional Q, British-style curves), Passive (Pultec-style simultaneous low boost
      and cut); optional air shelf.
- [ ] Saturation: add Transformer, Console and Exciter (harmonics on the highs only) to Tape, Tube and Clip.
- [ ] Limiter: Transparent, Punchy (soft-clip first), Loud; auto release.
- [x] Limiter true-peak ceiling (True Peak chooser, on by default).

## 3. Strip-wide character

- [x] Character switch on the strip: Clean, Analog, Tube, Tape, as a gentle stage after the slots, before Match
      and Out (soft saturation, slight high-frequency rolloff, low-end bump for Tape).
- [ ] Character amount knob, and a matching stage before the slots.
- [ ] Oversampling as one strip setting, passed by the mod to each unit.

## 4. Workflow

- [x] Presets: check that Bitwig's own container presets store the nested units and that the mod re-arms and the
      dropdowns match after a preset loads. (The mod now re-links the macro knobs when a slot's unit is replaced from
      outside, such as by a preset load.) Then a curated set: Vocal, Drum Bus, Bass, Acoustic, Mix Bus, Master.
- [x] Default chain on insert: Gain, EQ, Compressor, Saturation, Limiter (the mod loads the units into a new,
      empty strip).
- [ ] Default settings: tuned starting values per unit; "Save as default" in the mod. "Save as default" would be a mod
      feature (Bitwig has no per-device default preset).
- [x] Remember settings on swap: the mod keeps each slot's last values per unit type (for the session; not yet
      saved with the project).
- [ ] Reorder slots (drag or move left/right action, in the mod).
- [x] Auto gain match: a Match toggle by Out; the output stage follows the K-weighted short-term loudness
      difference between the strip's input and output (up to 24 dB, held in silence), with Out as a trim on top.
- [ ] Show the applied match gain on the output meter.
- [ ] A/B snapshots of the whole strip.
- [ ] Remote control pages for hardware controllers (macro knobs plus Out); check blueprint support.

## 5. New units

- [ ] Gate/Expander, De-esser, Transient Shaper, Clipper.
- [ ] Dynamic EQ (later).
- [ ] External sidechain into a nested unit: uncertain, needs a test of whether the container can expose a sidechain
      input. The compressor's internal sidechain filter already works.

## 6. Metering

- [ ] Scrolling level and gain-reduction history graph (TDR-style).
- [ ] Correlation/phase meter on the output.
- [ ] Integrated LUFS with reset and a target marker (for example -14 or -23).

## 7. Release

- [ ] Icon, manual/README with screenshots, release zip for Patchbay Launcher, demo project.
- [ ] Check other Bitwig versions (6.1.4) and Windows.

## Tried and set aside

- Speckled texture background (image panel item): works technically, did not look good. Code kept in
  `devices/common/texture.py`.
- Narrow Twentieth Century style glyphs: less legible than the original monoline set. Generator kept in
  `devices/common/glyphs.py`.
