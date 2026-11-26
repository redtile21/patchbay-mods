# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB gain pan width utility",
    "decimals": [
        ("Gain", "GAIN", -24.0, 24.0, 0.0, 1, "Output gain in dB", "gain_db"),
        ("Pan", "PAN", -100.0, 100.0, 0.0, 0, "Constant-power pan", "pan"),
        ("Width", "WIDTH", 0.0, 200.0, 100.0, 0, "Stereo width, 100 is unchanged", "stereo_width"),
    ],
    "cols": 1, "chooser_w": 20, "extra_w": 5, "display_w": 44,
    "knob_pos": [(0, 0), (0, 1), (0, 2)],
    "chooser_col": [(1, 9), (1, 25)],
    "free_labels": [(1, 3, 20, "POLARITY"), (1, 19, 20, "MONO")],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 27,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [
        ("Polarity", "POLARITY", ("Off", "L", "R", "Both"), 0, "Invert polarity", "polarity"),
        ("Mono", "MONO", ("Off", "On"), 0, "Sum to mono", "sum_mono"),
    ],
}
