# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB limiter ceiling",
    "decimals": [
        ("Input Gain", "INPUT_GAIN", 0.0, 24.0, 0.0, 1, "Input gain in dB", "input_gain"),
        ("Ceiling", "CEILING", -12.0, 0.0, -1.0, 1, "Output ceiling in dBFS", "ceiling"),
        ("Release", "RELEASE", 1.0, 1000.0, 100.0, 0, "Release time in ms", "release"),
        ("Lookahead", "LOOKAHEAD", 0.0, 5.0, 2.0, 1, "Lookahead in ms (adds latency)", "lookahead"),
        ("Stereo Link", "STEREO_LINK", 0.0, 100.0, 100.0, 0, "Detector stereo link in percent", "stereo_link"),
    ],
    "cols": 2, "display_w": 56,
    "titles": {"STEREO_LINK": "Link"},
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 15,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
