"""Give every control and display on a device's panels a help ID, for Bitwig's F1 device help.

The ID is "eb.<device>.<identifier>": the preset identifier of the parameter or drawing the item shows, lower case,
with slot numbers dropped (SLOT3_K1 -> slot_k1, MOVE_2 -> move), so the strip's slots share one help entry. Native
display items (a spectrum) get "eb.<device>.spectrum". The backdrop gets none. The text lives in the channel-strip
repository's help/help_text.py and is served by the eb-strip-console mod.
"""
import re

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import value as v


def _key(ident):
    ident = re.sub(r"^SLOT\d_", "SLOT_", ident)
    ident = re.sub(r"^MOVE_\d$", "MOVE", ident)
    return ident.lower()


def apply(doc, device):
    body = doc["body"]
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
        if ident and ident != "BACKDROP" and not f.get("help_id#10543", {}).get("value"):
            f["help_id#10543"] = v("String", f"eb.{device}.{_key(ident)}")
            f.setdefault("help_location#10546", v("Byte", 0))
        for name in ("items#6221",):
            for entry in f.get(name, {}).get("value", []) or []:
                visit(entry.get("Object") if isinstance(entry, dict) and "Object" in entry else entry)
        root = f.get("root_item#6212", {}).get("value")
        if root:
            visit(root)

    for entry in body["fields"]["panels#6213"]["value"]:
        visit(entry.get("Object", entry))
    return doc
