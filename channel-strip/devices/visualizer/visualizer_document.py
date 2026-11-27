"""EB Visualizer: spectrum, scrolling waveform, level history and stereo field.

Bitwig display items that work in a Patchbay device (tested 2026-11-27): the spectrum (spectrum analyser component)
and the scope observer, which is a scrolling time plot of its input over about 6 seconds (x 0..1). The sonogram and
the lightweight oscilloscope stayed blank. Three Nitro units in series (each at most 3 audio outputs, and each passes
the audio on so the engine keeps it running): levels (RMS, peak) -> mid -> field (8-band pan analysis, output).
"""
from __future__ import annotations

import hashlib
from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v
import unit_document2 as u

owned, settings, proxy, nitro_port, metadata = u.owned, u.settings, u.proxy, u.nitro_port, u.metadata
PANEL_HEIGHT = 53
REVISION = 3


def stack():
    return v("Object", obj(1803, "stack_panel_item_layout_settings", {"width#6217": v("Byte", 1), "height#6218": v("Byte", 1)}))


def common():
    return {"layout_settings#6226": stack(), "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True)}


def display(items, x_range, y_range, x_domain=0, y_domain=0, x_unit=0, y_unit=0):
    return obj(1804, "display_panel_item", {**common(), "items#6221": v("ObjectList", owned(*items)),
               "brightness#6245": v("Byte", 3), "x_min#6504": v("Double", x_range[0]), "x_max#6505": v("Double", x_range[1]),
               "x_domain#6506": v("Byte", x_domain), "x_unit#6507": v("Byte", x_unit), "y_min#6508": v("Double", y_range[0]),
               "y_max#6509": v("Double", y_range[1]), "y_domain#6510": v("Byte", y_domain), "y_unit#6511": v("Byte", y_unit),
               "left_margin_visible#10289": v("Bool", False), "right_margin_visible#10290": v("Bool", False),
               "top_margin_visible#10291": v("Bool", False), "bottom_margin_visible#10292": v("Bool", False)})


def axes():
    return obj(1805, "display_axes_panel_item", {**common(), "show_x_axis#6888": v("Bool", True), "show_y_axis#6889": v("Bool", True),
               "clip_x_axis_lines#6890": v("Bool", False), "clip_y_axis_lines#6891": v("Bool", False),
               "show_x_axis_label#6516": v("Bool", True), "show_y_axis_label#6517": v("Bool", False),
               "show_info_on_hover#6714": v("Bool", True)})


def label(text, x, y, w):
    return obj(1683, "label_panel_item", {"layout_settings#6226": v("Object", grid_layout(x, y, w, 4)),
               "text#6219": v("String", text), "color#6520": v("Int16", 1),
               "horizontal_alignment#6400": v("Byte", 1), "vertical_alignment#6401": v("Byte", 1)})


def place(item, x, y, w, h):
    item["fields"]["layout_settings#6226"] = v("Object", grid_layout(x, y, w, h))
    return item


def nitro(binary, connections, outputs):
    return obj(1721, "nitro_atom", {
        "settings#6194": settings(connections),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(nitro_port("in", 0, 2, output=False))),
        "nitro_outputs#15757": v("ObjectList", owned(*[nitro_port(n, k, ch, output=True) for k, (n, ch) in enumerate(outputs)]))})


def drawing(connections, name, shader):
    return obj(5512, "", {
        "settings#6194": settings(connections + [connection() for _ in range(9 - len(connections))]),
        "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
        "prevent_parent_from_sleeping#11002": v("Bool", False),
        "preset_identifier#701": v("String", name), "#16316": v("WideString", shader)})


def shader_item(ref_, x, y, w, h):
    return obj(5517, "", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
        "help_location#10546": v("Byte", 0), "data_model#6220": ref_})


def document(project, binaries, shaders):
    """binaries: {"levels", "mid", "field"} compiled Nitro; shaders: {"field", "grid", "frame"} SkSL source."""
    bindings = []

    def ref(target):
        wrapper = v("ObjectRef", 0)
        bindings.append((wrapper, "value", target))
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
        "name#3639": v("String", "In"), "preset_identifier#3640": v("String", "IN")})
    compensation = obj(1371, "delay_compensation_atom", {
        "settings#6194": settings([wire(input_proxy)]), "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0)})
    levels = nitro(binaries["levels"], [wire(compensation)], [("out", 2), ("rms", 2), ("peak", 2)])
    mid = nitro(binaries["mid"], [wire(levels, 0)], [("out", 2), ("mid", 2)])
    field = nitro(binaries["field"], [wire(mid, 0)], [("out", 2), ("display", 4), ("display2", 4)])
    analyser = obj(1851, "spectrum_analyser_component", {
        "settings#6194": settings([wire(field, 0)]), "channel_count#607": v("Byte", 0), "name#374": v("String", "Output"),
        "prevent_parent_from_sleeping#11002": v("Bool", False), "oversampling#13595": v("Byte", 0),
        "overlap#6571": v("Double", 0.5), "window_function#6573": v("Byte", 12)})

    def scope(source, port, name):
        return obj(1996, "scope_observer_component", {
            "settings#6194": settings([wire(source, port)]), "channel_count#607": v("Byte", 0), "name#374": v("String", name),
            "prevent_parent_from_sleeping#11002": v("Bool", False), "samples#7108": v("Int32", 1024)})
    sc_wave = scope(mid, 1, "Waveform")
    sc_rms = scope(levels, 1, "RMS")
    sc_peak = scope(levels, 2, "Peak")

    def plot(comp, color, tip):
        return obj(1997, "display_scope_observer_panel_item", {**common(), "tooltip_text#6867": v("String", tip),
                   "is_interactive#6499": v("Bool", False), "limit_to_display_range#11117": v("Bool", False),
                   "color#6518": v("Byte", color), "label#7100": v("String", ""), "component#7101": ref(comp),
                   "numeric_domain_x#7102": v("Byte", 0), "numeric_domain_y#7103": v("Byte", 0), "numeric_domain_z#7104": v("Byte", 0),
                   "draw_x_line#7105": v("Bool", False), "draw_y_line#7106": v("Bool", False), "dot_size#7107": v("Double", 1.0)})

    field_draw = drawing([wire(field, 1), wire(field, 2)], "FIELD_DRAWING", shaders["field"].replace("// @frame", shaders["frame"], 1))
    grid_draw = drawing([], "GRID_DRAWING", shaders["grid"])

    # Layout (grid units): title row, then the four displays; frames drawn by the backdrop.
    TOP, H = 6, PANEL_HEIGHT - 7
    cols = [("SPECTRUM", 64), ("WAVEFORM", 48), ("LEVEL", 48), ("STEREO", 36)]
    xs, x = [], 1
    for _, w in cols:
        xs.append(x)
        x += w + 1
    width = x
    items = []
    frames = [(xx - .3, TOP - .3, xx + w + .3, TOP + H + .3) for xx, (_, w) in zip(xs, cols)]
    backdrop = drawing([], "BACKDROP", u.backdrop_shader(width, frames))
    items.append(shader_item(ref(backdrop), 0, 0, width, PANEL_HEIGHT))
    for xx, (name, w) in zip(xs, cols):
        items.append(label(name, xx, 1, w))
    spec = u.spectrum_display(ref(analyser), (15.0, 135.0), (-84.0, -12.0))
    items.append(place(spec, xs[0], TOP, cols[0][1], H))
    items.append(place(display([plot(sc_wave, 4, "Waveform (mid), about the last 6 seconds")], (0.0, 1.0), (-1.0, 1.0)), xs[1], TOP, cols[1][1], H))
    items.append(place(display([plot(sc_rms, 4, "RMS level, about the last 6 seconds"), plot(sc_peak, 1, "Peak level, about the last 6 seconds")],
                               (0.0, 1.0), (0.0, 1.0)), xs[2], TOP, cols[2][1], H))
    items.append(shader_item(ref(grid_draw), xs[2], TOP, cols[2][1], H))
    items.append(shader_item(ref(field_draw), xs[3], TOP, cols[3][1], H))
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6), "brightness#6245": v("Byte", 0)})
    panel = obj(1680, "panel", {"name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
                "width#6232": v("Int16", width), "height#6233": v("Byte", PANEL_HEIGHT), "expressions#6277": v("ObjectList", owned())})
    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(field, 0)])
    identity = project["identity"]
    children = [backdrop, audio_source, compensation, levels, mid, field, analyser, sc_wave, sc_rms, sc_peak, field_draw, grid_draw]
    body = obj(151, "device_contents", {
        "child_components#173": v("ObjectList", owned(*children)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_in_ports#177": v("ObjectList", [{"ObjectRef": 0}, *owned(proxy(note=True))]),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", project["presentation"]["description"]),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", False), "suggest_for_audio_input#4847": v("Bool", True),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", REVISION), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", "elodea blackstar EB visualizer analyzer scope spectrum"),
        "device_type#391": v("Byte", 0), "has_been_modified#392": v("Bool", True),
        "color_tint#13354": v("Color", [0.0, 0.0, 0.0, 0.0])})
    bindings.append((body["fields"]["proxy_in_ports#177"]["value"][0], "ObjectRef", input_proxy))
    object_ids = {id(item): index for index, item in enumerate(iter_owned_objects(body), 1)}
    for wrapper, key, target in bindings:
        wrapper[key] = object_ids[id(target)]
    revision = hashlib.sha1(f"{identity['uuid']}/v{REVISION}".encode("utf-8")).hexdigest()
    return {"header": {"format_version": 3, "serialization_format": 2, "document_version": 207,
                       "object_offset": 0, "resources_offset": 0, "flags": 0},
            "metadata": metadata(project, revision), "body": body, "meta_nonce": "0" * 32, "body_nonce": "0" * 32}
