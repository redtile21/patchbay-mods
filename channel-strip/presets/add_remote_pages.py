"""Give an EB BlackStrip preset the standard remote control pages.

Bitwig keeps remote control pages with a device instance or preset (preset metadata field 6789,
remote_controls_preset_pages), not in the .bwdevice, so default pages ship as a preset. The input
must be a strip preset with at least one hand-made page holding SLOT1_K1, OUTPUT_GAIN, CHARACTER and
AB slots: their value types are copied for every slot.

    bwmodule-parser to-json in.bwpreset > in.json
    python3 add_remote_pages.py in.json out.json "Preset Name"
    bwmodule-parser from-json out.json out.bwpreset
"""
import copy
import json
import sys

LAYOUT = [
    ("Knob 1", [f"SLOT{n}_K1" for n in range(1, 7)] + ["OUTPUT_GAIN", "MATCH"]),
    ("Knob 2", [f"SLOT{n}_K2" for n in range(1, 7)] + ["CHARACTER_AMOUNT", "CHARACTER"]),
    ("Knob 3", [f"SLOT{n}_K3" for n in range(1, 7)] + ["CHARACTER_INPUT", "AB"]),
]
BOOLS = {"MATCH", "AB", "CHARACTER_INPUT", "VIEW"}


def main(src, dst, name):
    doc = json.load(open(src))
    meta = doc["body"]["fields"]["#5153"]["value"]["fields"]
    meta["preset_name#4830"]["value"] = name
    pages = meta["#6789"]["value"]["fields"]["#6782"]["value"]
    templates = {}
    for page in pages:
        for sl in page["Object"]["fields"]["#6778"]["value"]:
            templates[sl["Object"]["fields"]["#6780"]["value"].split("/")[1]] = sl

    def slot(ident, index):
        if ident.startswith("SLOT") or ident == "CHARACTER_AMOUNT":
            src_id = "SLOT1_K1"
        elif ident in BOOLS:
            src_id = "AB"
        else:
            src_id = ident
        s = copy.deepcopy(templates[src_id])
        f = s["Object"]["fields"]
        f["#6780"]["value"] = "CONTENTS/" + ident      # destination path
        f["#6792"]["value"] = index                     # slot index on the page
        f["#6779"]["value"] = ""                        # label ("" = the parameter's name)
        return s

    new = []
    for title, ids in LAYOUT:
        page = copy.deepcopy(pages[0])
        f = page["Object"]["fields"]
        f["#7017"]["value"] = title                     # page name
        f["#6778"]["value"] = [slot(i, k) for k, i in enumerate(ids)]
        new.append(page)
    meta["#6789"]["value"]["fields"]["#6782"]["value"] = new
    json.dump(doc, open(dst, "w"))


if __name__ == "__main__":
    main(*sys.argv[1:4])
