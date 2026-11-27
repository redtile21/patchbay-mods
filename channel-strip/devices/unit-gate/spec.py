# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB gate expander noise dynamics",
    "decimals": [
        ("Threshold", "THRESHOLD", -80.0, 0.0, -50.0, 1, "Threshold in dB", "threshold"),
        ("Range", "RANGE", 0.0, 80.0, 40.0, 0, "How far the gate closes, in dB", "range_db"),
        ("Hysteresis", "HYSTERESIS", 0.0, 12.0, 3.0, 1, "The gate closes this many dB below the threshold", "hysteresis"),
        ("Attack", "ATTACK", 0.05, 50.0, 0.5, 2, "Opening time in ms", "attack"),
        ("Hold", "HOLD", 0.0, 500.0, 50.0, 0, "Time kept open after the signal falls, in ms", "hold"),
        ("Release", "RELEASE", 5.0, 2000.0, 150.0, 0, "Closing time in ms", "release"),
        ("Sidechain HPF", "SC_HPF", 0.0, 500.0, 0.0, 0, "Detector high-pass in Hz, below 20 is off", "sc_hpf"),
    ],
    "cols": 3, "display_w": 80,
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)],
    "titles": {"SC_HPF": "SC HPF", "HYSTERESIS": "Hyst"},
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 6,
    # Option cells (shared frame): (column, row, title, controls[, width])
    "cells": [(1, 2, 'MODE', ['MODE'])],
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [
        ("Mode", "MODE", ("Gate", "Expander"), 0, "Gate: closes by the range below the threshold. Expander: 1:2 below the threshold, at most the range", "mode"),
    ],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
