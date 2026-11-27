"""F1 help for the EB devices, shown in Bitwig's own device help.

Keys are a panel item's help ID plus ".desc" (or ".title"). The device builds give every control the help ID
"eb.<device>.<identifier>" (see devices/common/help_ids.py); the strip's six slots share one entry per control.
Controls tied to a parameter get their title from Bitwig (name and range), so only displays need a ".title".
The eb-strip-console mod answers these keys (mod/gen_help.py writes them into HelpText.java).
"""

DISPLAY_UNIT = ("The left meter is the input and the right meter the output, each with a five-second peak hold and its "
                "peak in dB above it; numbers turn orange above 0 dB. ")

HELP = {
    # ---------------- EB Gain ----------------
    "eb.gain.gain": "Output level of the unit, in dB. 0 dB leaves the level unchanged.",
    "eb.gain.pan": "Constant-power pan: the centre keeps its level, and a hard pan sends everything to one side.",
    "eb.gain.width": "Stereo width: 0 % is mono, 100 % unchanged, 200 % twice the side signal for a wider image. "
                     "Width works on the mid and side signals, so the centre stays where it is.",
    "eb.gain.invert_l": "Inverts the polarity of the left channel. Use it to fix a channel recorded out of polarity.",
    "eb.gain.invert_r": "Inverts the polarity of the right channel.",
    "eb.gain.mono": "Sums left and right to mono, to check how a mix holds up in mono.",
    "eb.gain.panel_drawing.title": "Meters",
    "eb.gain.panel_drawing.desc": "Left and right level meters with five-second peak holds and their peaks in dB, then the pan "
                                  "position (marker, centre tick) and the width (bar, with a tick at 100 %).",

    # ---------------- EB EQ ----------------
    "eb.eq.hpf": "High-pass filter position, on a log scale from 20 Hz to 20 kHz. At 0 the filter is off.",
    "eb.eq.lpf": "Low-pass filter position, on a log scale from 20 Hz to 20 kHz. At 100 the filter is off.",
    "eb.eq.hp_slope": "High-pass slope: 6, 12 or 24 dB per octave.",
    "eb.eq.lp_slope": "Low-pass slope: 6, 12 or 24 dB per octave.",
    "eb.eq.low_gain": "Boost or cut of the low band, in dB.",
    "eb.eq.low_freq": "Frequency of the low band.",
    "eb.eq.low_q": "Slope of the low shelf, or width of the low bell (higher is narrower).",
    "eb.eq.low_shape": "Low band as a shelf (everything below the frequency) or a bell (around it).",
    "eb.eq.lm_gain": "Boost or cut of the low-mid bell, in dB.",
    "eb.eq.lm_freq": "Centre frequency of the low-mid bell.",
    "eb.eq.lm_q": "Width of the low-mid bell: higher is narrower.",
    "eb.eq.hm_gain": "Boost or cut of the high-mid bell, in dB.",
    "eb.eq.hm_freq": "Centre frequency of the high-mid bell.",
    "eb.eq.hm_q": "Width of the high-mid bell: higher is narrower.",
    "eb.eq.high_gain": "Boost or cut of the high band, in dB.",
    "eb.eq.high_freq": "Frequency of the high band.",
    "eb.eq.high_q": "Slope of the high shelf, or width of the high bell (higher is narrower).",
    "eb.eq.high_shape": "High band as a shelf (everything above the frequency) or a bell (around it).",
    "eb.eq.mode": "Clean: exact curves. Console: bells narrow as you boost or cut, and shelves get a small bump. "
                  "Passive: broad curves, and a low shelf boost also dips just above its frequency.",
    "eb.eq.air": "A broad high shelf at 14 kHz (+2, +4 or +6 dB) on top of the four bands, for open, airy highs.",
    "eb.eq.spectrum.title": "Response and spectrum",
    "eb.eq.spectrum.desc": "The output spectrum with the EQ's response curve on top: a yellow line for the filters and a "
                           "coloured line and point for each band.",
    "eb.eq.panel_drawing.title": "Response curve",
    "eb.eq.panel_drawing.desc": "The EQ's overall response, drawn over the output spectrum.",

    # ---------------- EB Compressor ----------------
    "eb.compressor.threshold": "Level above which compression starts, in dB.",
    "eb.compressor.ratio": "How strongly the level above the threshold is reduced: at 4:1, 4 dB over the threshold comes "
                           "out as 1 dB over.",
    "eb.compressor.attack": "How fast the compressor reacts once the level goes over the threshold, in ms. Slower lets "
                            "more of each transient through.",
    "eb.compressor.release": "How fast the compressor lets go once the level falls, in ms.",
    "eb.compressor.makeup": "Gain added after compression, to make up for the level it takes away.",
    "eb.compressor.knee": "Width of the soft knee in dB: compression eases in over this range around the threshold. "
                          "0 is a hard knee.",
    "eb.compressor.mix": "Dry/wet mix in percent. Below 100 % blends in the uncompressed signal (parallel compression).",
    "eb.compressor.sc_hpf": "High-pass filter on the detector only, in Hz, so the low end doesn't drive the compressor. "
                            "Below 20 Hz it is off.",
    "eb.compressor.stereo_link": "How much the two channels share the same gain reduction: 100 % keeps the stereo image "
                                 "steady, 0 % compresses each side on its own.",
    "eb.compressor.detector": "Peak follows every peak; RMS follows the average level for smoother compression. "
                              "Opto and Vari-Mu always use RMS.",
    "eb.compressor.mode": "Character of the compressor. VCA: clean and fast with a hard knee. Opto: smooth, with a "
                          "two-stage, program-dependent release. FET: very fast and gritty. Vari-Mu: gentle, with a soft "
                          "knee and a ratio that rises with level.",
    "eb.compressor.panel_drawing.title": "Transfer curve and meters",
    "eb.compressor.panel_drawing.desc": DISPLAY_UNIT + "The curve shows input level against output level, with the threshold "
                                        "as a line and a dot for the current level (orange while compressing). The orange bar "
                                        "hanging from the top is the gain reduction (GR), with its held value above it; THR "
                                        "is the threshold.",

    # ---------------- EB Saturation ----------------
    "eb.saturation.drive": "How hard the signal is pushed into the curve, in dB. More drive gives more harmonics and "
                           "more compression of the peaks.",
    "eb.saturation.bias": "Makes the curve asymmetric, which adds even harmonics (a warmer, thicker sound).",
    "eb.saturation.tone": "Tilt EQ around 1 kHz after the curve: negative is darker, positive brighter.",
    "eb.saturation.mix": "Dry/wet mix in percent. Below 100 % blends in the clean signal.",
    "eb.saturation.output": "Output level in dB.",
    "eb.saturation.type": "Tape: the highs saturate first, with a head bump around 75 Hz and a softer top as you drive "
                          "it. Tube: even harmonics that grow with the level. Soft Clip and Hard Clip: plain curves. "
                          "Transformer: the lows hit the core harder. Console: a gentle, forward knee. Exciter: adds "
                          "harmonics to the highs only. Diode Si: clean, then a hard knee. Diode Ge: soft, early and dark.",
    "eb.saturation.auto_gain": "Turns the output down as the drive goes up, so the level stays about the same and you "
                               "hear the change in tone rather than in loudness.",
    "eb.saturation.oversampling": "2x oversampling: the curve runs at twice the sample rate, which removes most of the "
                                  "aliasing (harsh, unrelated tones) when driven hard. Adds a few samples of delay. The "
                                  "strip's QUALITY switch sets it for every unit.",
    "eb.saturation.panel_drawing.title": "Curve and meters",
    "eb.saturation.panel_drawing.desc": DISPLAY_UNIT + "The curve shows how input maps to output with the current type, "
                                        "drive and bias, and the dot marks the current level.",

    # ---------------- EB Limiter ----------------
    "eb.limiter.input_gain": "Gain into the limiter, in dB: raise it to make the signal louder against the ceiling.",
    "eb.limiter.ceiling": "The highest level the output reaches, in dBFS.",
    "eb.limiter.release": "How fast the limiter recovers after a peak, in ms.",
    "eb.limiter.lookahead": "How far ahead the limiter looks, in ms, so it can turn down before a peak arrives. "
                            "Adds the same latency.",
    "eb.limiter.stereo_link": "How much the two channels share the same gain reduction: 100 % keeps the stereo image "
                              "steady.",
    "eb.limiter.mode": "Transparent limits cleanly. Punchy soft-clips the peaks first, so more of the punch survives. "
                       "Loud clips harder and releases faster.",
    "eb.limiter.auto_release": "Program-dependent release: short peaks recover fast, while sustained limiting recovers "
                               "slowly, to avoid pumping.",
    "eb.limiter.true_peak": "Also limits the peaks between samples (true peak), which can otherwise go over the ceiling "
                            "after conversion or encoding.",
    "eb.limiter.panel_drawing.title": "Transfer curve and meters",
    "eb.limiter.panel_drawing.desc": DISPLAY_UNIT + "The curve shows input against output, flattening at the ceiling "
                                     "(CEIL). The orange bar is the gain reduction (GR), with its held value above it.",

    # ---------------- EB Gate ----------------
    "eb.gate.threshold": "Level below which the gate closes, in dB.",
    "eb.gate.range": "How far the gate turns the signal down when closed, in dB.",
    "eb.gate.hysteresis": "The gate closes this many dB below the threshold, so it doesn't chatter on signals hovering "
                          "around it.",
    "eb.gate.attack": "How fast the gate opens, in ms.",
    "eb.gate.hold": "How long the gate stays open after the signal falls below the threshold, in ms.",
    "eb.gate.release": "How fast the gate closes, in ms.",
    "eb.gate.sc_hpf": "High-pass filter on the detector only, in Hz, so low rumble doesn't open the gate. Below 20 Hz "
                      "it is off.",
    "eb.gate.mode": "Gate: turns the signal down by the full range below the threshold. Expander: turns it down "
                    "gradually (1:2 below the threshold), at most by the range.",
    "eb.gate.panel_drawing.title": "Transfer curve and meters",
    "eb.gate.panel_drawing.desc": DISPLAY_UNIT + "The curve shows input against output, dropping below the threshold "
                                  "(THR). The orange bar is how far the gate is turning down (GR).",

    # ---------------- EB De-esser ----------------
    "eb.deesser.freq": "Frequency above which sibilance is detected and, in Split mode, turned down.",
    "eb.deesser.threshold": "Sibilance level above which the de-esser acts, in dB.",
    "eb.deesser.range": "The most the de-esser turns down, in dB.",
    "eb.deesser.release": "How fast the de-esser lets go after a sibilant, in ms.",
    "eb.deesser.mode": "Split: turns down only the band above the frequency. Wide: turns down the whole signal while "
                       "sibilance is detected.",
    "eb.deesser.spectrum.title": "Spectrum",
    "eb.deesser.spectrum.desc": "The output spectrum, with the de-esser's response drawn on top.",
    "eb.deesser.panel_drawing.title": "Response and meters",
    "eb.deesser.panel_drawing.desc": "The left meter (DET) is the detected sibilance with the threshold as a line, the right "
                                     "meter the output. The response shows the band being turned down (orange) and by how "
                                     "much right now; the orange bar is the gain reduction (GR). KHZ is the frequency.",

    # ---------------- EB Transient ----------------
    "eb.transient.attack": "More (positive) or less (negative) attack on each hit, in percent.",
    "eb.transient.sustain": "More (positive) or less (negative) sustain after each hit, in percent.",
    "eb.transient.output": "Output level in dB.",
    "eb.transient.mix": "Dry/wet mix in percent.",
    "eb.transient.speed": "How long a transient lasts: Fast for clicks and hats, Medium for most drums, Slow for toms "
                          "and bass.",
    "eb.transient.panel_drawing.title": "Envelope and meters",
    "eb.transient.panel_drawing.desc": DISPLAY_UNIT + "The curve shows a hit before (grey) and after (blue) shaping. The bar "
                                       "(GAIN) shows the gain change right now: up for more, down for less.",

    # ---------------- EB Clipper ----------------
    "eb.clipper.input_gain": "Gain into the clipper, in dB.",
    "eb.clipper.ceiling": "The level the clipper won't let the signal pass, in dBFS.",
    "eb.clipper.softness": "0 is a hard clip; higher values start rounding the peaks earlier, for a softer sound.",
    "eb.clipper.tilt": "Tilt EQ around 1 kHz before the clipper, undone after it: positive clips the highs harder, "
                       "negative the lows.",
    "eb.clipper.delta": "Listen to only what the clipper removes, to hear exactly what it does.",
    "eb.clipper.auto_gain": "Turns the output down by the input gain, so pushing into the clipper keeps the level matched.",
    "eb.clipper.oversampling": "2x oversampling: the clipper runs at twice the sample rate, which removes most of the "
                               "aliasing from hard clipping. Adds a few samples of delay. The strip's QUALITY switch sets it.",
    "eb.clipper.panel_drawing.title": "Transfer curve and meters",
    "eb.clipper.panel_drawing.desc": DISPLAY_UNIT + "The curve shows input against output, rounding into the ceiling (CEIL). "
                                     "The orange bar (CLIP) is how much is being clipped.",

    # ---------------- EB BlackStrip ----------------
    "eb.strip.slot_type": "The unit in this slot: Gain, EQ, Compressor, Saturation, Limiter, Gate, De-esser, Transient, "
                          "Clipper or Visualizer, or Bypass for an empty slot. Choosing one loads that unit (with the "
                          "EB Strip Console mod); each slot remembers its last settings per unit type for the session.",
    "eb.strip.slot_k1": "The slot's first macro knob, linked to the loaded unit's most important control (for example "
                        "Threshold on the Compressor). Its name and value are shown above it.",
    "eb.strip.slot_k2": "The slot's second macro knob, linked to one of the loaded unit's main controls.",
    "eb.strip.slot_k3": "The slot's third macro knob, linked to one of the loaded unit's main controls.",
    "eb.strip.move": "Swaps this slot with its neighbour, moving the units and their settings.",
    "eb.strip.slot_drawing.title": "Slot",
    "eb.strip.slot_drawing.desc": "The unit in the slot with its input and output levels, and its gain reduction on "
                                  "dynamics units. Below, the names and values of the three macro knobs.",
    "eb.strip.character": "A gentle colour stage after the slots: Clean, Analog (light console), Tube (even harmonics) "
                          "or Tape (soft highs, low bump).",
    "eb.strip.character_amount": "How strong the character is: 0 % is clean, 50 % the standard voicing, 100 % twice as "
                                 "much drive and colour.",
    "eb.strip.character_input": "Also adds the character on the way in, before the slots, like a console's input and "
                                "output stages.",
    "eb.strip.ab": "Flips between two complete versions of the strip (units, settings, Out, Match and Character). The "
                   "first flip makes B a copy of A. Kept for the session.",
    "eb.strip.oversampling": "2x oversampling for the whole strip: the Character stage, and the Saturation and Clipper "
                             "units in the slots, which follow this switch.",
    "eb.strip.in_meter.title": "Input meter",
    "eb.strip.in_meter.desc": "The strip's input level, with a five-second peak hold.",
    "eb.strip.out_meter.title": "Output meter",
    "eb.strip.out_meter.desc": "The output level with peak hold, and readouts: short-term loudness (LUFS), integrated "
                               "loudness (INT: green within 1 LU of the target, orange above, blue below), true peak, the "
                               "applied match gain (MATCH, while Match is on) and the stereo correlation bar (CORR, red "
                               "below zero).",
    "eb.strip.output_gain": "Output level of the strip, in dB. With Match on, it trims on top of the matched level.",
    "eb.strip.match": "Auto gain match: keeps the output as loud as the input (by K-weighted short-term loudness), so "
                      "you can judge the processing without being fooled by a level change.",
    "eb.strip.lufs_target": "Loudness target for the INT readout: -14 (streaming), -16 or -23 LUFS (broadcast), or Off.",
    "eb.strip.lufs_reset": "Restarts the integrated loudness measurement.",

    # ---------------- EB Visualizer ----------------
    "eb.visualizer.spectrum.title": "Spectrum",
    "eb.visualizer.spectrum.desc": "The live spectrum of the signal, with a frequency axis.",
    "eb.visualizer.waveform.title": "Waveform",
    "eb.visualizer.waveform.desc": "The mid (mono sum) signal, scrolling over about the last six seconds.",
    "eb.visualizer.level.title": "Level history",
    "eb.visualizer.level.desc": "RMS (blue) and peak (orange) level over about the last six seconds, from -60 dB at the "
                                "bottom to 0 dB at the top, with lines at -6, -12, -24 and -48 dB.",
    "eb.visualizer.grid_drawing.title": "Level history",
    "eb.visualizer.grid_drawing.desc": "RMS (blue) and peak (orange) level over about the last six seconds, from -60 dB at "
                                       "the bottom to 0 dB at the top, with lines at -6, -12, -24 and -48 dB.",
    "eb.visualizer.field_drawing.title": "Stereo field",
    "eb.visualizer.field_drawing.desc": "Eight frequency bands from 60 Hz (bottom) to 14 kHz (top). Each dot's position is "
                                        "the band's pan, its size and colour its level. The bar behind it is the band's "
                                        "width: none for mono, the whole field when the sides are unrelated, and red when "
                                        "the band goes out of phase (it will thin out in mono). The bar along the bottom is "
                                        "the overall correlation, red below zero.",
}
