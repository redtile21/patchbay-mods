"""EB Strip Spike: a container with six nested device chains in series."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v

# Reuse the verified helpers from the EB Gain builder.
_spec = importlib.util.spec_from_file_location("eb_gain_doc", Path(__file__).resolve().parents[1] / "eb-gain" / "demo_document.py")
_gain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gain)
owned, settings, proxy, parameter, indexed_parameter, nitro_port, metadata = (
    _gain.owned, _gain.settings, _gain.proxy, _gain.parameter, _gain.indexed_parameter, _gain.nitro_port, _gain.metadata)
value_port = _gain.value_port
boolean_parameter = _gain.boolean_parameter
KINDS = ("Bypass", "Gain", "EQ", "Compressor", "Saturation", "Limiter")

SLOTS = 6
SLOT_W, SLOT_H, GAP = 19, 8, 1
X0 = 7                      # slots start after the input meter
RIGHT_X = X0 + SLOTS * SLOT_W + (SLOTS - 1) * GAP + 1
RIGHT_W = 21
PANEL_WIDTH = RIGHT_X + RIGHT_W + 1
KNOB_Y = 16
METER_Y = 0
METER_H = 42
PANEL_HEIGHT = 53


def chooser(tip, ref, x, y, w):
    return obj(1714, "popup_chooser_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, 5)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tip), "data_model#6220": ref,
        "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", 0),
        "style#6266": v("Byte", 0), "color#7528": v("Int16", 6)})


def drawing_item(ref, x, y, w, h):
    return obj(5517, "", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
        "help_location#10546": v("Byte", 0), "data_model#6220": ref})


def knob_item(ref, x, y, w, h, size, title, tip):
    return obj(1687, "knob_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tip),
        "data_model#6220": ref, "title#6241": v("String", title),
        "knob_size#6223": v("Byte", size), "show_value_popup#10569": v("Bool", True),
        "attribute_id#11012": v("Int16", 712), "knob_style#7055": v("Byte", 3),
        "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", 6),
    })


def main_panel(drawing_refs, out_ref, type_refs, view_ref, in_meter_ref, out_meter_ref, knob_refs):
    items = []
    items.append(drawing_item(in_meter_ref, 0, METER_Y, X0 - 1, METER_H))
    items.append(obj(1702, "toggle_button_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(0, METER_Y + METER_H + 2, X0 - 1, 4)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", "Open or close the expanded view"), "data_model#6220": view_ref,
        "title#6241": v("String", "View"), "icon_name#6239": v("String", ""), "style#6240": v("Byte", 0),
        "label_style#6267": v("Byte", 0), "color#7527": v("Int16", 6)}))
    for i, tref in enumerate(type_refs):
        items.append(chooser(f"Slot {i + 1} unit", tref, X0 + i * (SLOT_W + GAP), 0, SLOT_W))
    for i, dref in enumerate(drawing_refs):
        sx = X0 + i * (SLOT_W + GAP)
        items.append(drawing_item(dref, sx, 6, SLOT_W, 8))
        items.append(drawing_item(dref, sx, KNOB_Y, SLOT_W, 36))   # the same drawing, tall: the knob names
        for k in range(3):
            items.append(knob_item(knob_refs[i][k], sx + 5, KNOB_Y + 12 * k, 9, 9, 1, "", f"Slot {i + 1} knob {k + 1}"))
    items.append(drawing_item(out_meter_ref, RIGHT_X, METER_Y, RIGHT_W, METER_H))
    items.append(knob_item(out_ref, RIGHT_X, METER_Y + METER_H + 1, 9, 9, 1, "Out", "Output gain in dB"))
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6),
        "brightness#6245": v("Byte", 1),
    })
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", PANEL_WIDTH), "height#6233": v("Byte", PANEL_HEIGHT),
        "expressions#6277": v("ObjectList", []),
    })


def slot(index, connections):
    return obj(587, "nested_device_chain_slot", {
        "settings#6194": settings(connections),
        "preset_identifier#836": v("String", f"SLOT{index}_CHAIN"),
        "name#835": v("String", f"Slot {index}"),
        "tooltip_text#2315": v("String", f"Device chain {index}"),
        "chain_color#10863": v("Byte", 0), "subtrack_sends_count#1374": v("Byte", 0),
        "sends_access_mode#12052": v("Byte", 0),
        "suggest_audio_input_devices#2435": v("Bool", True), "suggest_audio_output_devices#5769": v("Bool", True),
        "must_have_device_chain#2270": v("Bool", True),
        "suggest_note_input_devices#2434": v("Bool", False), "suggest_note_output_devices#5768": v("Bool", False),
        "show_mixer_as_subtrack#1373": v("Bool", False), "#2076": v("Bool", False),
        "has_volume_and_pan#2079": v("Bool", False), "#2077": v("Bool", False),
        "has_solo#2220": v("Bool", False), "has_note_led#9926": v("Bool", False),
        "should_devices_in_slot_determine_device_type#5361": v("Bool", False),
        "handle_pdc_separately#13583": v("Bool", False),
    })


def placeholder(connections):
    return obj(1437, "processing_delay_placeholder_component", {
        "settings#6194": settings(connections),
        "delay_in_samples#5331": v("Int32", 0), "placeholder_delay_unit#5333": v("Byte", 0),
        "include_input_latency#6435": v("Bool", False), "include_output_latency#5334": v("Bool", False),
        "include_block_size#7158": v("Bool", False),
    })


def stage(binary, connections):
    return obj(1721, "nitro_atom", {
        "settings#6194": settings(connections),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(
            nitro_port("in", 0, 2, output=False), nitro_port("gain_db", 1, 1, output=False))),
        "nitro_outputs#15757": v("ObjectList", owned(nitro_port("out", 0, 2, output=True))),
    })


def tap(binary, connections):
    inputs = [nitro_port("in", 0, 2, output=False), nitro_port("prev", 1, 2, output=False), value_port("kind", 2, boolean=False)]
    outputs = [nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True), nitro_port("display2", 2, 4, output=True)]
    return obj(1721, "nitro_atom", {
        "settings#6194": settings(connections),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(*outputs)),
    })


def meter_atom(binary, connections):
    inputs = [nitro_port("in", 0, 2, output=False)]
    outputs = [nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True), nitro_port("display2", 2, 4, output=True)]
    return obj(1721, "nitro_atom", {
        "settings#6194": settings(connections),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(*outputs)),
    })


def document(project, binary, tap_binary, meter_binary, shader, meter_shader):
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
    note_proxy = proxy(note=True)
    input_owner = wire(input_proxy)
    audio_source = obj(2000, "audio_source_atom", {
        "settings#6194": settings([input_owner]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "port_color#10378": v("Int16", 999),
        "name#3639": v("String", "In"), "preset_identifier#3640": v("String", "IN"),
    })
    compensation = obj(1371, "delay_compensation_atom", {
        "settings#6194": settings([wire(input_proxy)]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0),
    })
    out_gain = parameter("Output Gain", "OUTPUT_GAIN", -24.0, 24.0, 0.0, 1)
    view = boolean_parameter("Expanded View", "VIEW", False)
    knobs = [[parameter(f"Slot {i} Knob {k}", f"SLOT{i}_K{k}", 0.0, 100.0, 50.0, 0) for k in (1, 2, 3)] for i in range(1, SLOTS + 1)]
    types = [indexed_parameter(f"Slot {i}", f"SLOT{i}_TYPE", KINDS, 0) for i in range(1, SLOTS + 1)]
    def drawing_atom(meter, ident, code):
        return obj(5512, "", {
            "settings#6194": settings([wire(meter, 1), wire(meter, 2)] + [connection() for _ in range(7)]),
            "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
            "prevent_parent_from_sleeping#11002": v("Bool", False),
            "preset_identifier#701": v("String", ident), "#16316": v("WideString", code)})

    meter_in = meter_atom(meter_binary, [wire(compensation)])
    in_drawing = drawing_atom(meter_in, "IN_METER", meter_shader)
    previous = meter_in
    placeholders, slots, taps, drawings = [], [], [], []
    for index in range(1, SLOTS + 1):
        ph = placeholder([wire(previous), connection()])
        sl = slot(index, [wire(ph), wire(note_proxy)])
        tp = tap(tap_binary, [wire(sl), wire(previous), wire(types[index - 1])])
        drawing = obj(5512, "", {
            "settings#6194": settings([wire(tp, 1), wire(tp, 2)] + [connection() for _ in range(7)]),
            "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
            "prevent_parent_from_sleeping#11002": v("Bool", False),
            "preset_identifier#701": v("String", f"SLOT{index}_DRAWING"), "#16316": v("WideString", shader)})
        placeholders.append(ph)
        slots.append(sl)
        taps.append(tp)
        drawings.append(drawing)
        previous = tp
    stage_out = stage(binary, [wire(previous), wire(out_gain)])

    output_proxy = proxy(output=True)
    meter_out = meter_atom(meter_binary, [wire(stage_out)])
    out_drawing = drawing_atom(meter_out, "OUT_METER", meter_shader)
    output_proxy["fields"]["settings#6194"] = settings([wire(meter_out, 0)])
    panel = main_panel([ref(d) for d in drawings], ref(out_gain), [ref(t) for t in types], ref(view),
                       ref(in_drawing), ref(out_drawing), [[ref(k) for k in row] for row in knobs])
    identity = project["identity"]
    children = [audio_source, compensation, out_gain, *types, *[k for row in knobs for k in row], view, meter_in, in_drawing]
    for ph, sl, tp, dr in zip(placeholders, slots, taps, drawings):
        children += [ph, sl, tp, dr]
    children += [stage_out, meter_out, out_drawing]
    # Field order matters: the loader resolves references as it reads, so the
    # proxies must be owned (and read) before any component that points at them.
    body = obj(151, "device_contents", {
        "proxy_in_ports#177": v("ObjectList", owned(input_proxy, note_proxy)),
        "child_components#173": v("ObjectList", owned(*children)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", project["presentation"]["description"]),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", False), "suggest_for_audio_input#4847": v("Bool", True),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", 1), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", "elodea blackstar EB strip channel container"),
        "device_type#391": v("Byte", 0), "has_been_modified#392": v("Bool", True),
        "color_tint#13354": v("Color", [0.0, 0.0, 0.0, 0.0]),
    })
    object_ids = {id(item): index for index, item in enumerate(iter_owned_objects(body), 1)}
    for wrapper, key, target in bindings:
        wrapper[key] = object_ids[id(target)]
    revision = hashlib.sha1(f"{identity['uuid']}/v10".encode("utf-8")).hexdigest()
    meta = metadata({**project, "presentation": project["presentation"]}, revision)
    return {
        "header": {"format_version": 3, "serialization_format": 2, "document_version": 207,
                   "object_offset": 0, "resources_offset": 0, "flags": 0},
        "metadata": meta, "body": body, "meta_nonce": "0" * 32, "body_nonce": "0" * 32,
    }
