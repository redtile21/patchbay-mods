"""EB Blackstar Strip: six chain slots in series, input/output gain, per-slot bypass crossfade."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v

def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / rel)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
_gain = _load("eb-gain/demo_document.py", "eb_gain_doc")
owned, settings, proxy, parameter, indexed_parameter, nitro_port, value_port, metadata = (
    _gain.owned, _gain.settings, _gain.proxy, _gain.parameter, _gain.indexed_parameter,
    _gain.nitro_port, _gain.value_port, _gain.metadata)

SLOTS = 6
SW, GAP, EDGE = 44, 1, 17
PANEL_WIDTH = EDGE + SLOTS * (SW + GAP) + EDGE + 3
PANEL_HEIGHT = 53


def stage_core(binary, connections):
    inputs = [nitro_port("in", 0, 2, output=False)] + [nitro_port(f"k{j}", j, 1, output=False) for j in (1, 2, 3)]
    inputs.append(value_port("kind", 4, boolean=False))
    outputs = [nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True), nitro_port("display2", 2, 4, output=True)]
    return obj(1721, "nitro_atom", {
        "settings#6194": settings(connections),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0), "fft_order#6567": v("Byte", 0),
        "code_storage#10421": v("ByteArray", [0, *binary]), "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(*outputs)),
    })



KINDS = ("Bypass", "Gain", "EQ", "Compressor", "Saturation", "Limiter")


def slot_core(binary, connections, vectors=2):
    inputs = [nitro_port("in", 0, 2, output=False)] + [nitro_port(f"k{j}", j, 1, output=False) for j in (1, 2, 3)]
    inputs.append(value_port("kind", 4, boolean=False))
    outputs = [nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True), nitro_port("display2", 2, 4, output=True)]
    return obj(1721, "nitro_atom", {
        "settings#6194": settings(connections),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0), "fft_order#6567": v("Byte", 0),
        "code_storage#10421": v("ByteArray", [0, *binary]), "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(*outputs))})


def chooser(tip, ref, x, y, w):
    return obj(1714, "popup_chooser_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, 5)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tip), "data_model#6220": ref,
        "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", 0),
        "style#6266": v("Byte", 0), "color#7528": v("Int16", 6)})


def small_knob(title, tip, ref, x, y, w=14):
    return obj(1687, "knob_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, 12)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tip), "data_model#6220": ref, "title#6241": v("String", title),
        "knob_size#6223": v("Byte", 1), "show_value_popup#10569": v("Bool", True),
        "attribute_id#11012": v("Int16", 712), "knob_style#7055": v("Byte", 3),
        "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", 6)})


def spectrum_display(analyser_ref, x, y, w, h):
    def stack():
        return v("Object", obj(1803, "stack_panel_item_layout_settings", {"width#6217": v("Byte", 1), "height#6218": v("Byte", 1)}))
    common = lambda: {"layout_settings#6226": stack(), "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True)}
    spectrum = obj(1852, "display_spectrum_panel_item", {**common(), "analyzer_component#6574": analyser_ref,
                   "graph_style#6575": v("Byte", 1), "color#6577": v("Byte", 0), "tilt_spectrum#11093": v("Double", 4.5)})
    return obj(1804, "display_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "items#6221": v("ObjectList", owned(spectrum)),
        "brightness#6245": v("Byte", 3), "x_min#6504": v("Double", 15.0), "x_max#6505": v("Double", 135.0),
        "x_domain#6506": v("Byte", 2), "x_unit#6507": v("Byte", 4), "y_min#6508": v("Double", -42.0),
        "y_max#6509": v("Double", 18.0), "y_domain#6510": v("Byte", 1), "y_unit#6511": v("Byte", 2),
        "left_margin_visible#10289": v("Bool", False), "right_margin_visible#10290": v("Bool", False),
        "top_margin_visible#10291": v("Bool", False), "bottom_margin_visible#10292": v("Bool", False)})


def main_panel(slot_info, in_ref, out_ref):
    items = []
    for i, (type_ref, knob_refs, analyser_ref, drawing_ref) in enumerate(slot_info):
        x = EDGE + i * (SW + GAP)
        items.append(spectrum_display(analyser_ref, x, 8, SW, 24))
        items.append(obj(5517, "", {
            "layout_settings#6226": v("Object", grid_layout(x, 8, SW, 30)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
            "help_location#10546": v("Byte", 0), "data_model#6220": drawing_ref}))
        items.append(chooser(f"Slot {i + 1}: device or bypass", type_ref, x, 2, SW))
        for j, kr in enumerate(knob_refs):
            items.append(small_knob("", f"Slot {i + 1} knob {j + 1}", kr, x + 1 + j * 14, 39))
    items.append(small_knob("In", "Input gain in dB", in_ref, 2, 14, 15))
    items.append(small_knob("Out", "Output gain in dB", out_ref, PANEL_WIDTH - 17, 14, 15))
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""), "show_title#6243": v("Bool", False),
        "title_color#6522": v("Byte", 6), "brightness#6245": v("Byte", 1)})
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", PANEL_WIDTH), "height#6233": v("Byte", PANEL_HEIGHT),
        "expressions#6277": v("ObjectList", [])})


def document(project, binaries, shader):
    slot_bin = binaries[0]
    gain_bin = slot_bin
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

    input_proxy, note_proxy = proxy(), proxy(note=True)
    input_owner = connection()
    input_owner["Object"]["fields"]["source_component#248"] = v("Object", input_proxy)
    audio_source = obj(2000, "audio_source_atom", {
        "settings#6194": settings([input_owner]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "port_color#10378": v("Int16", 999),
        "name#3639": v("String", "In"), "preset_identifier#3640": v("String", "IN")})
    compensation = obj(1371, "delay_compensation_atom", {
        "settings#6194": settings([wire(input_proxy)]), "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0)})
    in_gain = parameter("Input Gain", "INPUT_GAIN", -24.0, 24.0, 0.0, 1)
    out_gain = parameter("Output Gain", "OUTPUT_GAIN", -24.0, 24.0, 0.0, 1)
    types = [indexed_parameter(f"Slot {i}", f"SLOT{i}_TYPE", KINDS, 0) for i in range(1, SLOTS + 1)]
    knobs = [[parameter(f"Slot {i} Knob {j}", f"SLOT{i}_K{j}", 0.0, 100.0, 50.0, 0) for j in (1, 2, 3)] for i in range(1, SLOTS + 1)]
    stage_kind = indexed_parameter("Stage", "STAGE_KIND", KINDS + ("Utility",), 6)
    stage_in = stage_core(gain_bin, [wire(compensation), wire(in_gain), connection(), connection(), wire(stage_kind)])

    previous = stage_in
    dsps, drawings, analysers = [], [], []
    for i in range(SLOTS):
        dsp = slot_core(slot_bin, [wire(previous), *(wire(k) for k in knobs[i]), wire(types[i])])
        drawing = obj(5512, "", {
            "settings#6194": settings([wire(dsp, 1), wire(dsp, 2)] + [connection() for _ in range(7)]),
            "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
            "prevent_parent_from_sleeping#11002": v("Bool", False),
            "preset_identifier#701": v("String", f"SLOT{i + 1}_DRAWING"), "#16316": v("WideString", shader)})
        analyser = obj(1851, "spectrum_analyser_component", {
            "settings#6194": settings([wire(dsp, 0)]), "channel_count#607": v("Byte", 0), "name#374": v("String", f"Slot {i + 1}"),
            "prevent_parent_from_sleeping#11002": v("Bool", False), "oversampling#13595": v("Byte", 0),
            "overlap#6571": v("Double", 0.5), "window_function#6573": v("Byte", 12)})
        dsps.append(dsp); drawings.append(drawing); analysers.append(analyser)
        previous = dsp
    stage_out = stage_core(gain_bin, [wire(previous), wire(out_gain), connection(), connection(), wire(stage_kind)])
    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(stage_out)])
    panel = main_panel([(ref(types[i]), [ref(k) for k in knobs[i]], ref(analysers[i]), ref(drawings[i])) for i in range(SLOTS)],
                       ref(in_gain), ref(out_gain))
    identity = project["identity"]
    children = [audio_source, compensation, in_gain, out_gain, stage_kind, *types, *(k for row in knobs for k in row), stage_in]
    for dsp, drawing, analyser in zip(dsps, drawings, analysers):
        children += [dsp, drawing, analyser]
    children.append(stage_out)
    body = obj(151, "device_contents", {
        "child_components#173": v("ObjectList", owned(*children)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_in_ports#177": v("ObjectList", [ref(input_proxy, list_entry=True), *owned(note_proxy)]),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", project["presentation"]["description"]),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", False), "suggest_for_audio_input#4847": v("Bool", True),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", 6), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", "elodea blackstar EB strip channel container"),
        "device_type#391": v("Byte", 0), "has_been_modified#392": v("Bool", True),
        "color_tint#13354": v("Color", [0.0, 0.0, 0.0, 0.0])})
    object_ids = {id(item): index for index, item in enumerate(iter_owned_objects(body), 1)}
    for wrapper, key, target in bindings:
        wrapper[key] = object_ids[id(target)]
    revision = hashlib.sha1(f"{identity['uuid']}/v6".encode()).hexdigest()
    meta = metadata({**project, "presentation": project["presentation"]}, revision)
    return {"header": {"format_version": 3, "serialization_format": 2, "document_version": 207,
                       "object_offset": 0, "resources_offset": 0, "flags": 0},
            "metadata": meta, "body": body, "meta_nonce": "0" * 32, "body_nonce": "0" * 32}
