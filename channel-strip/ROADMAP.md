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
- [x] Shared unit frame: every option (dropdown or switch) sits in a knob cell with an orange title over it
      (`cells` in the unit specs); every display names its meters and bars in a bottom caption row (IN, GR, OUT,
      CLIP, GAIN, DET) and the header readout beside it (THR, CEIL, KHZ), from the shared `common/frame.sksl`.
- [x] Remove the build digit in the corner of the unit displays.
- [x] Clearer slot states on the strip: a dimmed box for a bypassed slot, a gain-reduction bar on Compressor and
      Limiter slots (already in place; the slot output bar now uses the shared ramp).

## 2. Modes inside the existing units

Each mode is a chooser inside the same unit; knobs and automation stay the same, only the maths changes.

- [x] Compressor: VCA (clean, fast, hard knee), Opto (two-stage, program-dependent release), FET (very fast attack,
      aggressive, "all buttons" option), Vari-Mu (soft knee, ratio rises with level).
- [x] EQ: Clean (current), Console (proportional Q, shelves with a small bump), Passive (broad curves; a low shelf
      boost also dips just above it); Air shelf at 14 kHz (Off, +2, +4, +6 dB).
- [x] Saturation: add Transformer (lows hit the core harder), Console (gentle knee) and Exciter (harmonics on the
      highs only) to Tape, Tube and Clip; a DC blocker after the curve.
- [x] Limiter: Transparent, Punchy (soft-clip first), Loud (harder clip, faster release); Auto Rel (two-stage
      program-dependent release); True Peak is now an on/off button.
- [x] Limiter true-peak ceiling (True Peak chooser, on by default).

## 3. Strip-wide character

- [x] Character switch on the strip: Clean, Analog, Tube, Tape, as a gentle stage after the slots, before Match
      and Out (soft saturation, slight high-frequency rolloff, low-end bump for Tape).
- [x] Exact tanh (from exp) for Character and the compressor's drive.
- [x] Character amount knob, and a matching stage before the slots (Character column: chooser, Amount, Input switch).
- [x] Strip-wide 2x: a QUALITY switch in the Character column turns on 2x in Character and, through the mod, in the
      Saturation and Clipper units in the slots (also when a unit is loaded or swapped). True 2x oversampling with
      polyphase IIR half-band filters (`devices/common/halfband.py` generates the Nitro code); the dry paths (Mix,
      Clipper Delta) go through a matching pair so they stay in phase.
- [x] Saturation sound pass (from the saturation DSP guide): Tape with pre/de-emphasis, head bump and drive-dependent
      high loss; Tube bias that moves with level; Console asymmetric with emphasis; new Diode Si and Diode Ge types.
      Tried and dropped: ADAA and averaged in-between points (both leak a treble-heavy copy of the driven signal or dull
      the highs; measured in Python).

## 4. Workflow

- [x] Presets: check that Bitwig's own container presets store the nested units and that the mod re-arms and the
      dropdowns match after a preset loads. (The mod now re-links the macro knobs when a slot's unit is replaced from
      outside, such as by a preset load.) Then a curated set: Vocal, Drum Bus, Bass, Acoustic, Mix Bus, Master.
- [x] Default chain on insert: Gain, EQ, Compressor, Saturation, Limiter (the mod loads the units into a new,
      empty strip).
- [x] Default settings as presets (no "Save as default" in the mod): EB BlackStrip Default, Vocal, Drum Bus, Bass,
      Acoustic, Mix Bus, Master, built by `presets/make_presets.py` with named remote pages (Main, Shape, Detail).
- [x] Remember settings on swap: the mod keeps each slot's last values per unit type (for the session; not yet
      saved with the project).
- [x] Reorder slots: arrows beside each slot's top knob swap it with its neighbour; the mod moves the units and
      their settings (one MOVE_n button per neighbouring pair).
- [x] Auto gain match: a Match toggle by Out; the output stage follows the K-weighted short-term loudness
      difference between the strip's input and output (up to 24 dB, held in silence), with Out as a trim on top.
- [x] Show the applied match gain on the output meter (MATCH and the gain under True Peak, while Match is on).
- [x] A/B snapshots of the whole strip: an A/B switch in the Character column; flipping keeps the side you leave
      (units, settings, Out, Match, Character) and loads the other. Session only, not saved with the project.
- [x] View button in the device header (the window icon, as on Polysynth) instead of the VIEW toggle: the strip
      declares a maximized panel (`maximized_panel#7549`), which makes Bitwig show the icon; the mod hooks the window
      open (`JHy.MgQ(Z)`), closes Bitwig's window and opens the expanded view. A panel can't hold device chains
      (`nested_device_chain_slot_panel_item` is only a slot button), so the view stays a mod window.
- [x] Remote control pages: Bitwig keeps them with a device instance or preset, not in the .bwdevice, so they ship
      in the preset "EB BlackStrip Default" (pages Knob 1, Knob 2, Knob 3: the six slots' knob, plus Out/Match,
      Amount/Character, Input/A-B). `presets/add_remote_pages.py` adds them to any strip preset.

## 5. New units

- [x] Gate/Expander, De-esser, Transient Shaper, Clipper (EB Gate, EB De-esser, EB Transient, EB Clipper; scaffolded by
      `devices/common/new_units.py`).
- [x] De-esser: output spectrum behind the response curve (native display, as on the EQ).
- [x] Clipper: Tilt (shelf around 1 kHz before the clipper, undone after), Delta (hear only what is removed), Auto Gain
      (output down by the input gain).
- [x] Remember on/off switches on swap too (Clipper Delta and Auto Gain; Bitwig's boolean atom is `cbF`).

## 6. Metering

- [ ] EB Visualizer (`devices/visualizer`), a separate device: spectrum, scrolling waveform, level history (RMS and
      peak, about 6 s) and a stereo field (8 bands by pan and level, correlation bar). Built on the display items that
      work in a Patchbay device: the spectrum and the scope observer (a scrolling time plot). The sonogram and the
      lightweight oscilloscope stayed blank in tests. First build installed; needs checking in Bitwig.
- [x] Correlation meter on the output (bar under the readouts, red below zero).
- [x] Integrated LUFS (BS.1770 gated) as INT, a reset icon, and a target chooser (-14, -16, -23): green within
      1 LU, orange above.

## 7. Release

- [ ] Icon, manual/README with screenshots, release zip for Patchbay Launcher, demo project.
- [ ] Check other Bitwig versions (6.1.4) and Windows.

## Tried and set aside

- External sidechain and Dynamic EQ: not needed, Bitwig's modulators (Audio Sidechain, Follower) cover both.

- Speckled texture background (image panel item): works technically, did not look good. Code kept in
  `devices/common/texture.py`.
- Narrow Twentieth Century style glyphs: less legible than the original monoline set. Generator kept in
  `devices/common/glyphs.py`.
