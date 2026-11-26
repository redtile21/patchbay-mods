# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB clipper clip soft clip peaks loudness",
    "decimals": [
        ("Input Gain", "INPUT_GAIN", 0.0, 24.0, 0.0, 1, "Input gain in dB", "input_gain"),
        ("Ceiling", "CEILING", -12.0, 0.0, -1.0, 1, "Output ceiling in dBFS", "ceiling"),
        ("Softness", "SOFTNESS", 0.0, 100.0, 30.0, 0, "0 is a hard clip; higher starts rounding the peaks earlier", "softness"),
        ("Tilt", "TILT", -12.0, 12.0, 0.0, 1, "Tilt in dB around 1 kHz before the clipper, undone after it: positive clips the highs harder, negative the lows", "tilt"),
    ],
    "cols": 2, "display_w": 56,
    "titles": {"INPUT_GAIN": "Input"},
    "knob_pos": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 4,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [],
    # name, identifier, default, tooltip, nitro port, (column, y, width)
    "toggles": [
        ("Delta", "DELTA", False, "Listen to only what the clipper removes", "delta", (0, 26, 15)),
        ("Auto Gain", "AUTO_GAIN", False, "Turn the output down by the input gain, so driving the clipper keeps the level matched", "auto_gain", (1, 26, 15)),
    ],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
