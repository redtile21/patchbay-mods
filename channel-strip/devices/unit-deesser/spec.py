# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB de-esser deesser sibilance vocal dynamics",
    "decimals": [
        ("Frequency", "FREQ", 2000.0, 12000.0, 6000.0, 0, "Sibilance detector and split frequency in Hz", "freq"),
        ("Threshold", "THRESHOLD", -60.0, 0.0, -30.0, 1, "Threshold in dB", "threshold"),
        ("Range", "RANGE", 0.0, 24.0, 8.0, 1, "Most reduction in dB", "range_db"),
        ("Release", "RELEASE", 10.0, 500.0, 60.0, 0, "Release time in ms", "release"),
    ],
    "cols": 2, "display_w": 56,
    "titles": {"FREQ": "Freq"},
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 9,
    # Option cells (shared frame): (column, row, title, controls[, width])
    "cells": [(1, 2, 'MODE', ['MODE'])],
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [
        ("Mode", "MODE", ("Split", "Wide"), 0, "Split: turn down only above the frequency. Wide: turn down the whole signal", "mode"),
    ],
    # Output spectrum behind the response: 100 Hz .. 20 kHz (semitones, A4 = 69), -42 .. +18 dB, inside the display
    "native_display": "spectrum", "native_x": (43.35, 135.08), "native_rect": (9, 5, 32, 38),
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
