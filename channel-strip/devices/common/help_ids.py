"""Give every control and display on a device's panels a help ID, for Bitwig's F1 device help.

The ID is "eb.<device>.<identifier>": the preset identifier of the parameter or drawing the item shows, lower case,
with slot numbers dropped (SLOT3_K1 -> slot_k1, MOVE_2 -> move), so the strip's slots share one help entry. Only slot 1 carries it, and each entry is shown once, so the help
page describes one slot and the input and output columns instead of six copies. Native
display items (a spectrum) get "eb.<device>.spectrum". The backdrop gets none. Each control's callout goes on the side of the panel it sits on (help_location 0 would hide it). Each panel's root group gets "eb.<device>": Bitwig's help view only describes controls inside
a section (a group with a help ID), and the mod offers the root as that section. The text lives in the channel-strip
repository's help/help_text.py and is served by the eb-strip-console mod.
"""
import re

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import value as v


def _key(ident):
    ident = re.sub(r"^SLOT\d_", "SLOT_", ident)
    ident = re.sub(r"^MOVE_\d$", "MOVE", ident)
    return ident.lower()


def _repeat(ident):
    """The strip's slots 2-6 and the later swap buttons repeat slot 1's help; only slot 1 is described."""
    return bool(re.match(r"^SLOT[2-9]_", ident) or re.match(r"^MOVE_([2-9]|\d\d)$", ident))


def apply(doc, device):
    body = doc["body"]
    used = set()
    objects = list(iter_owned_objects(body))

    def target(field):
        if isinstance(field, dict) and field.get("type") == "ObjectRef":
            i = field.get("value")
            if isinstance(i, int) and 1 <= i <= len(objects):
                return objects[i - 1]
        return None

    def visit(item):
        if not isinstance(item, dict):
            return
        f = item.get("fields", {})
        ident = None
        for name in ("data_model#6220", "data_model#6742"):
            t = target(f.get(name))
            if t is not None:
                ident = t.get("fields", {}).get("preset_identifier#701", {}).get("value")
        if ident is None and item.get("class_id") == 1804 and "help_id#10543" not in f:
            ident = "SPECTRUM"
        key = f"eb.{device}.{_key(ident)}" if ident else None
        if (ident and ident != "BACKDROP" and not _repeat(ident) and key not in used
                and not f.get("help_id#10543", {}).get("value")):
            f["help_id#10543"] = v("String", key)
            used.add(key)
        if f.get("help_id#10543", {}).get("value", "").count(".") >= 2:
            helped.append(f)
        for name in ("items#6221",):
            for entry in f.get(name, {}).get("value", []) or []:
                visit(entry.get("Object") if isinstance(entry, dict) and "Object" in entry else entry)
        root = f.get("root_item#6212", {}).get("value")
        if root:
            # The root group is the device's one help section (the mod offers it to the help view).
            rf = (root.get("Object", root) if isinstance(root, dict) else {}).get("fields", {})
            if isinstance(rf, dict) and not rf.get("help_id#10543", {}).get("value"):
                rf["help_id#10543"] = v("String", f"eb.{device}")
            visit(root)

    for entry in body["fields"]["panels#6213"]["value"]:
        helped = []
        visit(entry.get("Object", entry))
        # Where Bitwig puts each control's callout: 0 none (never shown), 1 left, 2 right, 3 top, 4 bottom.
        # Controls in the left half of the panel get theirs on the left, the rest on the right.
        boxes = [_box(f) for f in helped]
        right = max((b[0] + b[2] for b in boxes if b), default=0)
        for f, b in zip(helped, boxes):
            side = 1 if b and b[0] + b[2] / 2 < right / 2 else 2
            f["help_location#10546"] = v("Byte", side)
    return doc


def _box(fields):
    ls = fields.get("layout_settings#6226", {}).get("value")
    lf = (ls or {}).get("fields", {}) if isinstance(ls, dict) else {}
    try:
        return tuple(lf[k]["value"] for k in ("x#6215", "y#6216", "width#6217", "height#6218"))
    except (KeyError, TypeError):
        return None
