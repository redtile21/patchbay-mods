# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB transient shaper attack sustain punch drums dynamics",
    "decimals": [
        ("Attack", "ATTACK", -100.0, 100.0, 0.0, 0, "More (positive) or less (negative) attack, in percent", "attack"),
        ("Sustain", "SUSTAIN", -100.0, 100.0, 0.0, 0, "More (positive) or less (negative) sustain, in percent", "sustain"),
        ("Output", "OUTPUT", -24.0, 6.0, 0.0, 1, "Output level in dB", "output"),
        ("Mix", "MIX", 0.0, 100.0, 100.0, 0, "Dry/wet mix in percent", "mix"),
    ],
    "cols": 2, "display_w": 56,
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 9,
    # Option cells (shared frame): (column, row, title, controls[, width])
    "cells": [(1, 2, 'SPEED', ['SPEED'])],
    "meters": {}, "vectors": 2, "display_h": 51,
    "choices": [
        ("Speed", "SPEED", ("Fast", "Medium", "Slow"), 1, "How long a transient lasts: Fast for clicks and hats, Slow for toms and bass", "speed"),
    ],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
