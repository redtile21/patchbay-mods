# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB saturation distortion clip drive",
    "decimals": [
        ("Drive", "DRIVE", 0.0, 36.0, 0.0, 1, "Drive in dB", "drive"),
        ("Bias", "BIAS", -1.0, 1.0, 0.0, 2, "Asymmetry, adds even harmonics", "bias"),
        ("Tone", "TONE", -6.0, 6.0, 0.0, 1, "Tilt: negative darker, positive brighter, in dB", "tone"),
        ("Mix", "MIX", 0.0, 100.0, 100.0, 0, "Dry/wet mix in percent", "mix"),
        ("Output", "OUTPUT", -24.0, 6.0, 0.0, 1, "Output level in dB", "output"),
    ],
    "cols": 2, "display_w": 56,
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)],
    "chooser_col": [(1, 28), (1, 34), (1, 40)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 19,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [
        ("Type", "TYPE", ("Tape", "Tube", "Soft Clip", "Hard Clip", "Transformer", "Console", "Exciter"), 0,
         "Saturation curve. Transformer thickens the lows, Console is gentle, Exciter adds harmonics to the highs only", "sat_type"),
        ("Auto Gain", "AUTO_GAIN", ("Auto Off", "Auto On"), 0, "Compensate level for drive", "auto_gain"),
        ("Oversampling", "OVERSAMPLING", ("1x OS", "2x OS"), 0, "Oversampling", "oversampling"),
    ],
}
