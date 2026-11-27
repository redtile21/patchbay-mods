"""Build the EB BlackStrip factory presets.

Each preset is a strip with a unit in each slot, the unit settings, the strip's macro knobs set to match, and
remote control pages whose controls are named after what they do in that preset ("Comp Thresh", not "Slot 3 Knob 1").

Bitwig stores every nested unit as a full copy of its state (values plus embedded display data), so units are not
built from scratch: they are copied from saved strip presets (decoded with bwmodule-parser to-json) that hold one of
each unit type at default settings, and only their values are changed.

    python3 make_presets.py OUT_DIR DEVICES_DIR templates/units-b.json templates/units-a.json
(units-b is first: its remote page provides the page and slot templates). A preset also stores each display's shader
code; DEVICES_DIR (the installed .bwdevice files) supplies the current code, so presets show the current panels.
writes OUT_DIR/<name>.json for each preset; encode with `bwmodule-parser from-json`.
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNIT_DIRS = {"Gain": "gain", "EQ": "eq", "Compressor": "compressor", "Saturation": "saturation", "Limiter": "limiter",
             "Gate": "gate", "De-esser": "deesser", "Transient": "transient", "Clipper": "clipper"}
KINDS = ("Bypass", "Gain", "EQ", "Compressor", "Saturation", "Limiter", "Gate", "De-esser", "Transient", "Clipper", "Visualizer")

# The strip's three macro knobs per unit (as the mod links them) and their short names on a controller, in the
# order they matter most (rank 0 goes on the first remote page).
SHORT = {"Gain": "Gain", "EQ": "EQ", "Compressor": "Comp", "Saturation": "Sat", "Limiter": "Lim", "Gate": "Gate",
         "De-esser": "DeEss", "Transient": "Trans", "Clipper": "Clip"}
KNOBS = {   # unit -> (param of knob 1, 2, 3), "ENHANCE" is the EQ's low and high gain together (0..6 dB)
    "Gain": ("GAIN", "PAN", "WIDTH"), "EQ": ("LPF", "HPF", "ENHANCE"), "Compressor": ("THRESHOLD", "RATIO", "MAKEUP"),
    "Saturation": ("DRIVE", "TONE", "MIX"), "Limiter": ("INPUT_GAIN", "CEILING", "RELEASE"),
    "Gate": ("THRESHOLD", "RANGE", "RELEASE"), "De-esser": ("FREQ", "THRESHOLD", "RANGE"),
    "Transient": ("ATTACK", "SUSTAIN", "OUTPUT"), "Clipper": ("INPUT_GAIN", "CEILING", "SOFTNESS"),
}
RANK = {    # unit -> knob numbers (1..3) from most to least useful
    "Gain": (1, 3, 2), "EQ": (2, 3, 1), "Compressor": (1, 2, 3), "Saturation": (1, 3, 2), "Limiter": (1, 2, 3),
    "Gate": (1, 2, 3), "De-esser": (2, 1, 3), "Transient": (1, 2, 3), "Clipper": (1, 2, 3),
}
LABEL = {"GAIN": "Gain", "PAN": "Pan", "WIDTH": "Width", "LPF": "LPF", "HPF": "HPF", "ENHANCE": "Enhance",
         "THRESHOLD": "Thresh", "RATIO": "Ratio", "MAKEUP": "Makeup", "DRIVE": "Drive", "TONE": "Tone", "MIX": "Mix",
         "INPUT_GAIN": "Input", "CEILING": "Ceiling", "RELEASE": "Release", "RANGE": "Range", "FREQ": "Freq",
         "ATTACK": "Attack", "SUSTAIN": "Sustain", "OUTPUT": "Output", "SOFTNESS": "Soft"}
ENHANCE_DB = 6.0


def hpf(hz):
    """EQ high/low-pass knob position (0..100, log 20 Hz .. 20 kHz) for a frequency."""
    return round(math.log(hz / 20.0) / 0.06907755, 2)


def spec(unit):
    ns = {}
    exec((HERE.parent / "devices" / f"unit-{UNIT_DIRS[unit]}" / "spec.py").read_text(), ns)
    return ns["SPEC"]


# ---- the presets: slots (unit, {param: value}), strip settings ----
PRESETS = {
    "EB BlackStrip Default": {
        "slots": [("Gain", {}), ("EQ", {}), ("Compressor", {}), ("Saturation", {}), ("Limiter", {}), None],
    },
    "Vocal": {
        "slots": [
            ("Gain", {}),
            ("EQ", {"HPF": hpf(80), "HP_SLOPE": "12 dB", "LOW_SHAPE": "Bell", "LOW_GAIN": -2.5, "LOW_FREQ": 280,
                    "LOW_Q": 1.2, "HM_GAIN": 2.0, "HM_FREQ": 3200, "HM_Q": 0.9, "HIGH_GAIN": 1.5, "HIGH_FREQ": 10000,
                    "MODE": "Console", "AIR": "Air +2"}),
            ("Compressor", {"MODE": "Opto", "THRESHOLD": -22, "RATIO": 3, "ATTACK": 10, "RELEASE": 120, "MAKEUP": 4}),
            ("De-esser", {"FREQ": 6500, "THRESHOLD": -30, "RANGE": 6, "RELEASE": 60}),
            ("Saturation", {"TYPE": "Tube", "DRIVE": 6, "MIX": 35, "AUTO_GAIN": True}),
            None,
        ],
    },
    "Drum Bus": {
        "slots": [
            ("Transient", {"ATTACK": 25, "SUSTAIN": -10}),
            ("EQ", {"HPF": hpf(25), "LOW_GAIN": 2, "LOW_FREQ": 60, "LM_GAIN": -1.5, "LM_FREQ": 400,
                    "HIGH_GAIN": 2, "HIGH_FREQ": 10000}),
            ("Compressor", {"MODE": "VCA", "THRESHOLD": -18, "RATIO": 4, "ATTACK": 30, "RELEASE": 100, "MAKEUP": 3,
                            "MIX": 60, "SC_HPF": 80}),
            ("Saturation", {"TYPE": "Tape", "DRIVE": 8, "MIX": 50, "AUTO_GAIN": True}),
            ("Clipper", {"INPUT_GAIN": 2, "CEILING": -1, "SOFTNESS": 40, "AUTO_GAIN": True}),
            None,
        ],
    },
    "Bass": {
        "slots": [
            ("Gain", {}),
            ("EQ", {"HPF": hpf(30), "LOW_GAIN": 2, "LOW_FREQ": 80, "LM_GAIN": -3, "LM_FREQ": 250, "LM_Q": 1.2,
                    "HM_GAIN": 2, "HM_FREQ": 900}),
            ("Compressor", {"MODE": "Opto", "THRESHOLD": -20, "RATIO": 4, "ATTACK": 20, "RELEASE": 150, "MAKEUP": 4}),
            ("Saturation", {"TYPE": "Transformer", "DRIVE": 8, "MIX": 60, "AUTO_GAIN": True}),
            ("Clipper", {"CEILING": -1, "SOFTNESS": 50}),
            None,
        ],
    },
    "Acoustic": {
        "slots": [
            ("EQ", {"HPF": hpf(70), "LOW_SHAPE": "Bell", "LOW_GAIN": -3, "LOW_FREQ": 220, "LOW_Q": 1.2,
                    "HM_GAIN": 1.5, "HM_FREQ": 4000, "HIGH_GAIN": 2, "HIGH_FREQ": 12000}),
            ("Compressor", {"MODE": "Opto", "THRESHOLD": -20, "RATIO": 2.5, "ATTACK": 15, "RELEASE": 150, "MAKEUP": 2}),
            ("Saturation", {"TYPE": "Tape", "DRIVE": 3, "MIX": 30, "AUTO_GAIN": True}),
            None, None, None,
        ],
    },
    "Mix Bus": {
        "slots": [
            ("EQ", {"MODE": "Console", "LOW_GAIN": 1, "LOW_FREQ": 60, "HIGH_GAIN": 1, "HIGH_FREQ": 12000, "AIR": "Air +2"}),
            ("Compressor", {"MODE": "VCA", "THRESHOLD": -12, "RATIO": 2, "ATTACK": 30, "RELEASE": 100, "MAKEUP": 1.5,
                            "SC_HPF": 60}),
            ("Saturation", {"TYPE": "Console", "DRIVE": 3, "AUTO_GAIN": True}),
            None, None, None,
        ],
        "strip": {"CHARACTER": "Analog", "CHARACTER_AMOUNT": 40.0},
    },
    "Master": {
        "slots": [
            ("EQ", {"HPF": hpf(22), "HP_SLOPE": "12 dB"}),
            ("Compressor", {"MODE": "VCA", "THRESHOLD": -8, "RATIO": 1.5, "ATTACK": 30, "RELEASE": 200, "KNEE": 12,
                            "MAKEUP": 1, "SC_HPF": 60}),
            ("Saturation", {"TYPE": "Tape", "DRIVE": 2, "MIX": 30, "AUTO_GAIN": True}),
            ("Clipper", {"CEILING": -0.5, "SOFTNESS": 50}),
            ("Limiter", {"MODE": "Transparent", "INPUT_GAIN": 2, "CEILING": -1, "AUTO_RELEASE": True, "TRUE_PEAK": True}),
            None,
        ],
    },
}
STRIP_CHOICES = {"CHARACTER": ("Clean", "Analog", "Tube", "Tape")}


def fields(o):
    return o["Object"]["fields"] if "Object" in o else o["fields"]


def children(meta):
    return meta["#164"]["value"]["fields"]["child_presets#524"]["value"]


def ident(cp):
    return fields(cp)["identifier#697"]["value"]


def load_templates(paths):
    units, base = {}, None
    for p in paths:
        doc = json.load(open(p))
        base = base or doc
        meta = doc["body"]["fields"]["#5153"]["value"]["fields"]
        for cp in children(meta):
            if ident(cp).endswith("_CHAIN"):
                for u in fields(cp)["#2273"]["value"]["fields"]["#841"]["value"]["fields"]["#135"]["value"]:
                    name = fields(u)["#154"]["value"]
                    units.setdefault(name[3:], u)          # "EB Compressor" -> "Compressor"
    return base, units


def set_value(cp, value, choices=None):
    f = fields(cp)
    if "value#310" in f:
        f["value#310"]["value"] = float(value)
    elif "#303" in f:
        f["#303"]["value"] = bool(value)
    elif "value#627" in f:
        f["value#627"]["value"] = choices.index(value) if isinstance(value, str) else int(value)
    else:
        raise KeyError(ident(cp))


def build_unit(template, unit, values):
    u = copy.deepcopy(template)
    sp = spec(unit)
    defaults = {d[1]: d[4] for d in sp["decimals"]}
    defaults.update({c[1]: c[2][c[3]] for c in sp["choices"]})
    defaults.update({t[1]: t[2] for t in sp.get("toggles", [])})
    choices = {c[1]: c[2] for c in sp["choices"]}
    unknown = set(values) - set(defaults)
    if unknown:
        raise KeyError(f"{unit}: no parameter {sorted(unknown)}")
    for cp in children(fields(u)):
        i = ident(cp)
        if i in defaults:
            set_value(cp, values.get(i, defaults[i]), choices.get(i))
    return u, {**defaults, **values}


def knob_pct(unit, k, vals):
    p = KNOBS[unit][k]
    if p == "ENHANCE":
        return max(0.0, min(1.0, vals["LOW_GAIN"] / ENHANCE_DB)) * 100.0
    d = next(d for d in spec(unit)["decimals"] if d[1] == p)
    return max(0.0, min(1.0, (vals[p] - d[2]) / (d[3] - d[2]))) * 100.0


def remote_pages(meta, slots):
    """Three pages: the most useful knob of every loaded unit, then the next, then the last; strip controls fill up."""
    pages = meta["#6789"]["value"]["fields"]["#6782"]["value"]
    templates = {}
    for page in pages:
        for sl in fields(page)["#6778"]["value"]:
            templates[fields(sl)["#6780"]["value"].split("/")[1]] = sl
    def slot(target, label, index, kind):
        s = copy.deepcopy(templates[kind])
        f = fields(s)
        f["#6780"]["value"] = "CONTENTS/" + target
        f["#6792"]["value"] = index
        f["#6779"]["value"] = label
        return s
    extras = [[("OUTPUT_GAIN", "Out", "OUTPUT_GAIN"), ("MATCH", "Match", "AB")],
              [("CHARACTER_AMOUNT", "Char Amount", "SLOT1_K1"), ("CHARACTER", "Character", "CHARACTER")],
              [("CHARACTER_INPUT", "Char Input", "AB"), ("AB", "A/B", "AB")]]
    new = []
    for rank, title in enumerate(("Main", "Shape", "Detail")):
        entries = []
        for n, s in enumerate(slots, start=1):
            if s is None:
                continue
            unit = s[0]
            k = RANK[unit][rank]
            label = {"GAIN": "Trim", "PAN": "Pan", "WIDTH": "Width"}[KNOBS[unit][k - 1]] if unit == "Gain" \
                else f"{SHORT[unit]} {LABEL[KNOBS[unit][k - 1]]}"
            entries.append((f"SLOT{n}_K{k}", label, "SLOT1_K1"))
        entries = entries[:6] + extras[rank]
        page = copy.deepcopy(pages[0])
        f = fields(page)
        f["#7017"]["value"] = title
        f["#6778"]["value"] = [slot(t, lab, i, kind) for i, (t, lab, kind) in enumerate(entries)]
        new.append(page)
    meta["#6789"]["value"]["fields"]["#6782"]["value"] = new


def build(name, recipe, base, units):
    doc = copy.deepcopy(base)
    meta = doc["body"]["fields"]["#5153"]["value"]["fields"]
    meta["preset_name#4830"]["value"] = name
    slots = recipe["slots"]
    strip_vals = {"OUTPUT_GAIN": 0.0, "MATCH": False, "CHARACTER": "Clean", "CHARACTER_AMOUNT": 50.0,
                  "CHARACTER_INPUT": False, "AB": False, **{f"MOVE_{n}": False for n in range(1, 6)}}
    strip_vals.update(recipe.get("strip", {}))
    knob_vals = {}
    for n, s in enumerate(slots, start=1):
        strip_vals[f"SLOT{n}_TYPE"] = KINDS.index(s[0]) if s else 0
        for k in range(3):
            knob_vals[f"SLOT{n}_K{k + 1}"] = 50.0
    unit_objs = {}
    for n, s in enumerate(slots, start=1):
        if s is None:
            continue
        unit, values = s
        obj, vals = build_unit(units[unit], unit, values)
        unit_objs[n] = obj
        for k in range(3):
            knob_vals[f"SLOT{n}_K{k + 1}"] = round(knob_pct(unit, k, vals), 4)
    strip_vals.update(knob_vals)
    for cp in children(meta):
        i = ident(cp)
        if i in strip_vals:
            set_value(cp, strip_vals[i], STRIP_CHOICES.get(i, KINDS))
        elif i.endswith("_CHAIN"):
            n = int(i[4])
            lst = fields(cp)["#2273"]["value"]["fields"]["#841"]["value"]["fields"]["#135"]
            lst["value"] = [unit_objs[n]] if n in unit_objs else []
    # The VIEW toggle is gone (the header window button opens the expanded view): drop its stored value.
    kids = meta["#164"]["value"]["fields"]["child_presets#524"]
    kids["value"] = [cp for cp in kids["value"] if ident(cp) != "VIEW"]
    remote_pages(meta, slots)
    refresh_shaders(meta, SHADERS.get("EB BlackStrip", {}))
    for obj in unit_objs.values():
        refresh_shaders(fields(obj), SHADERS.get(fields(obj)["#154"]["value"], {}))
    return doc


CODEC = Path.home() / "Developer/bitwig-blueprint-work/bitwig-devices-blueprint/tools/document_codec/target/release/bwmodule-parser"


def current_shaders(devices_dir):
    """device name -> drawing identifier -> shader source, from the installed .bwdevice files."""
    import subprocess
    out = {}
    for f in Path(devices_dir).glob("EB *.bwdevice"):
        body = json.loads(subprocess.run([str(CODEC), "to-json", str(f)], capture_output=True, check=True, text=True).stdout)["body"]
        name = body["fields"]["device_name#386"]["value"]
        codes = {}
        for c in body["fields"]["child_components#173"]["value"]:
            o = c["Object"] if "Object" in c else c
            if o["class_id"] == 5512 and "#16316" in o["fields"]:
                codes[o["fields"]["preset_identifier#701"]["value"]] = o["fields"]["#16316"]["value"]
        out[name] = codes
    return out


def refresh_shaders(meta, codes):
    for cp in children(meta):
        o = cp["Object"] if "Object" in cp else cp
        if o["class_id"] == 5516 and ident(cp) in codes:
            o["fields"]["#16331"]["value"] = codes[ident(cp)]


SHADERS = {}


def main(out_dir, devices_dir, *template_paths):
    SHADERS.update(current_shaders(devices_dir))
    base, units = load_templates(template_paths)
    missing = set(UNIT_DIRS) - set(units)
    if missing:
        raise SystemExit(f"templates lack {sorted(missing)}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, recipe in PRESETS.items():
        json.dump(build(name, recipe, base, units), open(out / f"{name}.json", "w"))
        print("built", name)


if __name__ == "__main__":
    main(*sys.argv[1:])
