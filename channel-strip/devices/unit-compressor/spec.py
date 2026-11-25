# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB compressor dynamics",
    "decimals": [
        ("Threshold", "THRESHOLD", -60.0, 0.0, -18.0, 1, "Threshold in dB", "threshold"),
        ("Ratio", "RATIO", 1.0, 20.0, 4.0, 1, "Compression ratio", "ratio"),
        ("Attack", "ATTACK", 0.1, 100.0, 10.0, 1, "Attack time in ms", "attack"),
        ("Release", "RELEASE", 10.0, 2000.0, 100.0, 0, "Release time in ms", "release"),
        ("Makeup", "MAKEUP", 0.0, 24.0, 0.0, 1, "Makeup gain in dB", "makeup"),
        ("Knee", "KNEE", 0.0, 24.0, 6.0, 1, "Soft knee width in dB", "knee"),
        ("Mix", "MIX", 0.0, 100.0, 100.0, 0, "Dry/wet mix in percent", "mix"),
        ("Sidechain HPF", "SC_HPF", 0.0, 300.0, 0.0, 0, "Detector high-pass in Hz, below 20 is off", "sc_hpf"),
        ("Stereo Link", "STEREO_LINK", 0.0, 100.0, 100.0, 0, "Detector stereo link in percent", "stereo_link"),
    ],
    "cols": 3, "display_w": 80,
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (2, 3)],
    "titles": {"SC_HPF": "SC HPF", "STEREO_LINK": "Link"},
    "chooser_col": [(1, 36), (1, 29)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 21,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [
        ("Detector", "DETECTOR", ("Peak", "RMS"), 0, "Detector type (Opto and Vari-Mu always use RMS)", "detector"),
        ("Mode", "MODE", ("VCA", "Opto", "FET", "Vari-Mu"), 0, "Compressor character: VCA clean, Opto smooth, FET fast and gritty, Vari-Mu gentle", "mode"),
    ],
}
