# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB gain pan width utility",
    "decimals": [
        ("Gain", "GAIN", -24.0, 24.0, 0.0, 1, "Output gain in dB", "gain_db"),
        ("Pan", "PAN", -100.0, 100.0, 0.0, 0, "Constant-power pan", "pan"),
        ("Width", "WIDTH", 0.0, 200.0, 100.0, 0, "Stereo width, 100 is unchanged", "stereo_width"),
    ],
    "cols": 1, "chooser_w": 20, "extra_w": 5, "display_w": 16,
    "knob_pos": [(0, 0), (0, 1), (0, 2)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 32,
    # Option cells (shared frame): (column, row, title, controls[, width])
    "cells": [(1, 0, 'POLARITY', ['INVERT_L', 'INVERT_R'], 20), (1, 1, 'MONO', ['MONO'], 20)],
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [],
    # name, identifier, default, tooltip, nitro port, (column, y, width), icon, label style
    "toggles": [
        ("L", "INVERT_L", False, "Invert the left channel's polarity", "invert_l", None, "phase.svg", 2),
        ("R", "INVERT_R", False, "Invert the right channel's polarity", "invert_r", None, "phase.svg", 2),
        ("Mono", "MONO", False, "Sum to mono", "sum_mono", None, "mono.svg"),
    ],
}
