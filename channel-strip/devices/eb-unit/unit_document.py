"""Generic EB unit device: decimal knobs + choice parameters + one Nitro core + stereo display.

Parameters are wired to Nitro inports in this order: `in`, decimals (audio inports), choices (i32 value inports).
Panel: knobs in two rows on the left, choosers and the shader display in a right-hand block.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v

_spec = importlib.util.spec_from_file_location("eb_gain_doc", Path(__file__).resolve().parents[1] / "eb-gain" / "demo_document.py")
_g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_g)
owned, settings, proxy, parameter, indexed_parameter, nitro_port, value_port, metadata = (
    _g.owned, _g.settings, _g.proxy, _g.parameter, _g.indexed_parameter, _g.nitro_port, _g.value_port, _g.metadata)

KNOB_W, KNOB_H, KNOB_PITCH = 21, 22, 22
PANEL_HEIGHT = 53
SIDE_W = 32


def panel_width(spec):
    cols = (len(spec["decimals"]) + 1) // 2
    return 3 + cols * KNOB_PITCH + 2 + SIDE_W + 2


def main_panel(spec, knob_refs, choice_refs, drawing_ref):
    cols = (len(spec["decimals"]) + 1) // 2
    items = []
    for i, (dec, ref) in enumerate(zip(spec["decimals"], knob_refs)):
        col, row = i % cols, i // cols
        items.append(obj(1687, "knob_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(3 + col * KNOB_PITCH, 2 + row * 25, KNOB_W, KNOB_H)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", dec[6]), "data_model#6220": ref, "title#6241": v("String", dec[0]),
            "knob_size#6223": v("Byte", 3), "show_value_popup#10569": v("Bool", True),
            "attribute_id#11012": v("Int16", 712), "knob_style#7055": v("Byte", 3),
            "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", 6),
        }))
    side_x = 3 + cols * KNOB_PITCH + 2
    for i, (ch, ref) in enumerate(zip(spec["choices"], choice_refs)):
        items.append(obj(1714, "popup_chooser_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(side_x, 2 + i * 6, SIDE_W, 5)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", ch[4]), "data_model#6220": ref,
            "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", 0),
            "style#6266": v("Byte", 7), "color#7528": v("Int16", 6),
        }))
    top = 2 + len(spec["choices"]) * 6
    items.append(obj(5517, "", {
        "layout_settings#6226": v("Object", grid_layout(side_x, top, SIDE_W, PANEL_HEIGHT - top - 3)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
        "help_location#10546": v("Byte", 0), "data_model#6220": drawing_ref,
    }))
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6), "brightness#6245": v("Byte", 0),
    })
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", panel_width(spec)), "height#6233": v("Byte", PANEL_HEIGHT),
        "expressions#6277": v("ObjectList", []),
    })


def document(spec, project, binary, shader):
    bindings = []

    def ref(target, *, list_entry=False):
        key = "ObjectRef" if list_entry else "value"
        wrapper = {"ObjectRef": 0} if list_entry else v("ObjectRef", 0)
        bindings.append((wrapper, key, target))
        return wrapper

    def wire(target, port=0):
        entry = connection(port=port)
        entry["Object"]["fields"]["source_component#248"] = ref(target)
        return entry

    input_proxy = proxy()
    input_owner = connection()
    input_owner["Object"]["fields"]["source_component#248"] = v("Object", input_proxy)
    audio_source = obj(2000, "audio_source_atom", {
        "settings#6194": settings([input_owner]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "port_color#10378": v("Int16", 999),
        "name#3639": v("String", "In"), "preset_identifier#3640": v("String", "IN"),
    })
    compensation = obj(1371, "delay_compensation_atom", {
        "settings#6194": settings([wire(input_proxy)]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0),
    })
    decs = [parameter(d[0], d[1], d[2], d[3], d[4], d[5]) for d in spec["decimals"]]
    chs = [indexed_parameter(c[0], c[1], c[2], c[3]) for c in spec["choices"]]
    n_dec = len(decs)
    inputs = [nitro_port("in", 0, 2, output=False)]
    inputs += [nitro_port(d[7], 1 + i, 1, output=False) for i, d in enumerate(spec["decimals"])]
    inputs += [value_port(c[5], 1 + n_dec + i, boolean=False) for i, c in enumerate(spec["choices"])]
    dsp = obj(1721, "nitro_atom", {
        "settings#6194": settings([wire(compensation), *(wire(p) for p in decs), *(wire(c) for c in chs)]),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(
            nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True))),
    })
    drawing = obj(5512, "", {
        "settings#6194": settings([wire(dsp, 1), *(connection() for _ in range(8))]),
        "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
        "prevent_parent_from_sleeping#11002": v("Bool", False),
        "preset_identifier#701": v("String", "PANEL_DRAWING"), "#16316": v("WideString", shader),
    })
    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(dsp, 0)])
    panel = main_panel(spec, [ref(p) for p in decs], [ref(c) for c in chs], ref(drawing))
    identity = project["identity"]
    kw = project["presentation"]["description"]
    body = obj(151, "device_contents", {
        "child_components#173": v("ObjectList", owned(audio_source, compensation, *decs, *chs, dsp, drawing)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_in_ports#177": v("ObjectList", [ref(input_proxy, list_entry=True), *owned(proxy(note=True))]),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", kw),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", False), "suggest_for_audio_input#4847": v("Bool", True),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", 1), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", spec["keywords"]),
        "device_type#391": v("Byte", 0), "has_been_modified#392": v("Bool", True),
        "color_tint#13354": v("Color", [0.0, 0.0, 0.0, 0.0]),
    })
    object_ids = {id(item): index for index, item in enumerate(iter_owned_objects(body), 1)}
    for wrapper, key, target in bindings:
        wrapper[key] = object_ids[id(target)]
    revision = hashlib.sha1(f"{identity['uuid']}/v1".encode("utf-8")).hexdigest()
    return {
        "header": {"format_version": 3, "serialization_format": 2, "document_version": 207,
                   "object_offset": 0, "resources_offset": 0, "flags": 0},
        "metadata": metadata(project, revision), "body": body, "meta_nonce": "0" * 32, "body_nonce": "0" * 32,
    }
