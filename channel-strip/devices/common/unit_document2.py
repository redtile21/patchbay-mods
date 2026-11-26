"""EB unit device v2: size-2 knob grid, native stereo peak meters, one or two shader display vectors.

Spec keys: decimals, choices, keywords, cols (knob columns), meters ("in"/"out" bools), vectors (1 or 2),
display_w (grid width of the display), display_h.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v
from devices.common.metal_knob import knob_overlay

_spec = importlib.util.spec_from_file_location("eb_gain_doc", Path(__file__).resolve().parents[1] / "eb-gain" / "demo_document.py")
_g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_g)
owned, settings, proxy, parameter, indexed_parameter, nitro_port, value_port, metadata = (
    _g.owned, _g.settings, _g.proxy, _g.parameter, _g.indexed_parameter, _g.nitro_port, _g.value_port, _g.metadata)
boolean_parameter = _g.boolean_parameter

PANEL_HEIGHT = 53
KNOB_W, KNOB_H, PITCH_X, PITCH_Y = 19, 14, 20, 16
METER_W = 6
CAP_CY, CAP_R = 3.66, 2.17      # the native knob's cap inside its rectangle (measured on a screenshot), grid units
TOP = 3
# Bitwig display colours (RCp): 1 orange, 4 blue, 6 white, 10 mint. Chooser styles (Gpo): 0 button, 1 display, 4 flat, 7 plain.
TITLE_COLOR = 1
CHOOSER_COLOR = 4
CHOOSER_STYLE = 1


def geometry(spec):
    dw = spec.get("display_w", 34)
    x = 2
    g = {"dw": dw}
    if spec.get("layout") == "bar":
        g["disp_x"] = 2
        g["bottom_y"] = TOP + spec["display_h"] + 1
        g["side_x"] = 2 + dw + 2
        g["width"] = (g["side_x"] + spec.get("side_cols", 0) * PITCH_X + 2) if spec.get("side_cols") else dw + 4
        return g
    if "knob_pos" in spec:
        g["pos"] = True
    if spec["meters"].get("in"):
        g["in_x"] = x
        x += METER_W + 1
    g["disp_x"] = x
    x += dw + 1
    if spec["meters"].get("out"):
        g["out_x"] = x
        x += METER_W + 1
    g["knob_x"] = x + 2
    ncols = (max([c for c, r in spec["knob_pos"]] + [c for c, y in spec.get("chooser_col", [])]) + 1) if "knob_pos" in spec else spec["cols"]
    g["width"] = g["knob_x"] + ncols * spec.get("pitch_x", PITCH_X) + 2 + spec.get("extra_w", 0)
    return g


def vu_meter(connections):
    return obj(40, "vu_meter_atom", {
        "settings#6194": settings(connections), "channel_count#607": v("Byte", 0), "scale_style#2075": v("Int32", 0)})


def main_panel(spec, g, knob_refs, choice_refs, drawing_ref, in_vu, out_vu, display_item=None, expressions=(), backdrop_ref=None, overlay=None, toggle_refs=()):
    items = []
    knob_rects = []
    if backdrop_ref is not None:
        items.append(obj(5517, "", {
            "layout_settings#6226": v("Object", grid_layout(0, 0, g["width"], PANEL_HEIGHT)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
            "help_location#10546": v("Byte", 0), "data_model#6220": backdrop_ref}))
    cols = spec["cols"]
    disp_h = spec.get("display_h", PANEL_HEIGHT - 2 * TOP)
    choosers_h = 6 if "chooser_abs" in spec else (0 if (spec.get("layout") == "bar" or "chooser_pos" in spec or "chooser_col" in spec) else 6 * len(spec["choices"]))
    for name, vu, key in (("Input peak meter", in_vu, "in_x"), ("Output peak meter", out_vu, "out_x")):
        if vu is not None:
            items.append(obj(1724, "meter_panel_item", {
                "layout_settings#6226": v("Object", grid_layout(g[key], TOP, METER_W, PANEL_HEIGHT - 2 * TOP)),
                "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
                "tooltip_text#6867": v("String", name), "data_model#6742": vu,
                "meter_style#6738": v("Int32", 0), "meter_origin#6739": v("Int32", 2)}))
    def shader_item():
        return obj(5517, "", {
            "layout_settings#6226": v("Object", grid_layout(g["disp_x"], TOP, g["dw"], disp_h - choosers_h)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
            "help_location#10546": v("Byte", 0), "data_model#6220": drawing_ref})
    if display_item is not None:
        nx, ny, nw, nh = spec.get("native_rect", (0, 0, g["dw"], disp_h - choosers_h))
        display_item["fields"]["layout_settings#6226"] = v("Object", grid_layout(g["disp_x"] + nx, TOP + ny, nw, nh))
        items.append(display_item)
        if drawing_ref is not None:
            items.append(shader_item())
    else:
        items.append(shader_item())
    bar = spec.get("layout") == "bar"
    nb = spec.get("n_bottom", 0)
    kp = spec.get("knob_pos")
    for i, (dec, ref) in enumerate(zip(spec["decimals"], knob_refs)):
        if bar:
            if i < nb:
                kx, ky = 2 + i * PITCH_X + (g["dw"] - nb * PITCH_X) // 2, g["bottom_y"]
            else:
                j = i - nb
                kx, ky = g["side_x"] + (j % spec["side_cols"]) * PITCH_X, TOP + (j // spec["side_cols"]) * PITCH_Y
        elif kp:
            kx, ky = g["knob_x"] + kp[i][0] * spec.get("pitch_x", PITCH_X), TOP + spec.get("row0", 0) + int(kp[i][1] * spec.get("pitch_y", PITCH_Y))
        else:
            kx, ky = g["knob_x"] + (i % cols) * PITCH_X, TOP + (i // cols) * PITCH_Y
        knob_rects.append((kx, ky, spec.get("knob_w", KNOB_W), spec.get("knob_h", KNOB_H), dec))
        items.append(obj(1687, "knob_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(kx, ky, spec.get("knob_w", KNOB_W), spec.get("knob_h", KNOB_H))),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", dec[6]), "data_model#6220": ref, "title#6241": v("String", spec.get("titles", {}).get(dec[1], dec[0])),
            "knob_size#6223": v("Byte", spec.get("knob_size", 2)), "show_value_popup#10569": v("Bool", True),
            "attribute_id#11012": v("Int16", 712), "knob_style#7055": v("Byte", 3),
            "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", 6)}))
    for (lc, ltext) in spec.get("section_labels", []):
        items.append(obj(1683, "label_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(g["knob_x"] + lc * spec.get("pitch_x", PITCH_X), TOP, spec.get("pitch_x", PITCH_X) - 1, 5)),
            "text#6219": v("String", ltext), "color#6520": v("Int16", spec.get("section_color", TITLE_COLOR)),
            "horizontal_alignment#6400": v("Byte", 1), "vertical_alignment#6401": v("Byte", 1)}))
    for (lc, ly, lw, ltext) in spec.get("free_labels", []):
        items.append(obj(1683, "label_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(g["knob_x"] + lc * spec.get("pitch_x", PITCH_X), ly, lw, 5)),
            "text#6219": v("String", ltext), "color#6520": v("Int16", TITLE_COLOR),
            "horizontal_alignment#6400": v("Byte", 1), "vertical_alignment#6401": v("Byte", 1)}))
    for (lx, lw, ltext) in spec.get("chooser_labels", []):
        lx = g["disp_x"] + lx if lx >= 0 else g["disp_x"] + g["dw"] + lx
        items.append(obj(1683, "label_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(lx, TOP + disp_h - choosers_h + 1, lw, 5)),
            "text#6219": v("String", ltext), "color#6520": v("Int16", TITLE_COLOR),
            "horizontal_alignment#6400": v("Byte", 1), "vertical_alignment#6401": v("Byte", 1)}))
    for i, (ch, ref) in enumerate(zip(spec["choices"], choice_refs)):
        if bar:
            n_side = len(spec["decimals"]) - nb
            cx, cy, cw = g["side_x"], TOP + ((n_side + spec["side_cols"] - 1) // spec["side_cols"]) * PITCH_Y + 1 + i * 6, spec["side_cols"] * PITCH_X - 1
        elif "chooser_col" in spec:
            col, cy = spec["chooser_col"][i]
            cx, cw = g["knob_x"] + col * spec.get("pitch_x", PITCH_X), spec.get("chooser_w", spec.get("knob_w", KNOB_W))
        elif "chooser_abs" in spec:
            ax, ay, cw = spec["chooser_abs"][i]
            cx = g["disp_x"] + ax if ax is not None else g["disp_x"] + g["dw"] - cw
            cy = TOP + disp_h - choosers_h + 1 + ay
        elif "chooser_pos" in spec:
            cx, cy, cw = g["knob_x"] + spec["chooser_pos"][i][0] * PITCH_X, TOP + spec["chooser_pos"][i][1] * PITCH_Y + 4, KNOB_W
        else:
            cx, cy, cw = g["disp_x"], TOP + disp_h - choosers_h + i * 6 + 1, g["dw"]
        items.append(obj(1714, "popup_chooser_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(cx, cy, cw, 5)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", ch[4]), "data_model#6220": ref,
            "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", 0),
            "style#6266": v("Byte", spec.get("chooser_styles", {}).get(i, CHOOSER_STYLE)),
            "color#7528": v("Int16", spec.get("chooser_colors", {}).get(i, CHOOSER_COLOR))}))
    for tg, ref in zip(spec.get("toggles", []), toggle_refs):
        col, ty, tw = tg[5]
        items.append(obj(1702, "toggle_button_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(g["knob_x"] + col * spec.get("pitch_x", PITCH_X), TOP + ty, tw, 5)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", tg[3]), "data_model#6220": ref, "title#6241": v("String", tg[0]),
            "icon_name#6239": v("String", ""), "style#6240": v("Byte", 0), "label_style#6267": v("Byte", 0),
            "color#7527": v("Int16", 6)}))
    if overlay is not None:
        extra_items, extra_exprs = overlay(knob_rects)
        items.extend(extra_items)
        expressions = list(expressions) + list(extra_exprs)
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6), "brightness#6245": v("Byte", 0)})
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", g["width"]), "height#6233": v("Byte", PANEL_HEIGHT),
        "expressions#6277": v("ObjectList", owned(*expressions))})


def eq_display(analyser_ref, ref):
    """Native display: log frequency axis, spectrum of the output, band lines and EQ points.
    Returns (display item, panel expressions). Frequencies are drawn in semitone units (A4 = 69 at 440 Hz)."""
    def stack():
        return v("Object", obj(1803, "stack_panel_item_layout_settings", {"width#6217": v("Byte", 1), "height#6218": v("Byte", 1)}))
    common = lambda: {"layout_settings#6226": stack(), "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True)}
    spectrum = obj(1852, "display_spectrum_panel_item", {**common(), "analyzer_component#6574": analyser_ref,
                   "graph_style#6575": v("Byte", 1), "color#6577": v("Byte", 0), "tilt_spectrum#11093": v("Double", 4.5)})
    axes = obj(1805, "display_axes_panel_item", {**common(), "show_x_axis#6888": v("Bool", True), "show_y_axis#6889": v("Bool", True),
               "clip_x_axis_lines#6890": v("Bool", False), "clip_y_axis_lines#6891": v("Bool", False),
               "show_x_axis_label#6516": v("Bool", True), "show_y_axis_label#6517": v("Bool", False),
               "show_info_on_hover#6714": v("Bool", True)})
    items, exprs = [spectrum, axes], []
    def line(tooltip, color, expr):
        it = obj(1807, "display_line_panel_item", {**common(), "tooltip_text#6867": v("String", tooltip),
                 "is_interactive#6499": v("Bool", False), "limit_to_display_range#11117": v("Bool", False),
                 "color#6518": v("Byte", color), "offset#6497": v("Double", 60.0), "component#6503": v("NullObject"),
                 "is_horizontal#6498": v("Bool", True), "line_thickness#13800": v("Double", 1.0),
                 "paint_outline#13801": v("Bool", False)})
        items.append(it); exprs.append((expr, it, 6497))
    note = lambda p: f"69.0 + 12.0 * ({p} / 440.0).log2"
    # filter knobs are 0..100 log positions: f = 20 * 1000^(p/100)
    line("High-Pass", 2, "15.4868206 + 1.19589411 * HPF")
    line("Low-Pass", 2, "15.4868206 + 1.19589411 * LPF")
    for tip, fp, gp, col in (("Low", "LOW_FREQ", "LOW_GAIN", 1), ("Low-Mid", "LM_FREQ", "LM_GAIN", 3),
                             ("High-Mid", "HM_FREQ", "HM_GAIN", 4), ("High", "HIGH_FREQ", "HIGH_GAIN", 5)):
        line(tip + " frequency", col, note(fp))
        pt = obj(1806, "display_point_panel_item", {**common(), "offset_x#6500": v("Double", 60.0), "offset_y#6501": v("Double", 0.0),
                 "is_interactive#6499": v("Bool", False), "show_modulated_value#6730": v("Bool", False)})
        items.append(pt); exprs.append((note(fp), pt, 6500)); exprs.append((gp, pt, 6501))
    disp = obj(1804, "display_panel_item", {**common(), "items#6221": v("ObjectList", owned(*items)),
               "brightness#6245": v("Byte", 3), "x_min#6504": v("Double", 15.0), "x_max#6505": v("Double", 135.0),
               "x_domain#6506": v("Byte", 2), "x_unit#6507": v("Byte", 4), "y_min#6508": v("Double", -42.0),
               "y_max#6509": v("Double", 18.0), "y_domain#6510": v("Byte", 1), "y_unit#6511": v("Byte", 2),
               "left_margin_visible#10289": v("Bool", False), "right_margin_visible#10290": v("Bool", False),
               "top_margin_visible#10291": v("Bool", False), "bottom_margin_visible#10292": v("Bool", False)})
    return disp, exprs


def backdrop_shader(width, frames):
    """Flat charcoal panel with thin framed sections (the TDR look); frames are (x0, y0, x1, y1) in grid units."""
    rects = "\n".join(f"    d = min(d, frame(p, float2({a:.2f}, {b:.2f}), float2({c:.2f}, {e:.2f}), .5));" for a, b, c, e in frames)
    return f"""float frame(float2 p, float2 lo, float2 hi, float r) {{
    float2 c = (lo + hi) * .5;
    float2 h = (hi - lo) * .5;
    float2 q = abs(p - c) - h + r;
    return length(max(q, 0.)) + min(max(q.x, q.y), 0.) - r;
}}

half4 main(float2 fragCoord) {{
    float2 p = fragCoord / iResolution.xy * float2({float(width):.1f}, {float(PANEL_HEIGHT):.1f});
    float3 col = float3(.128, .133, .143);
    float a = 1.;
    float3 well = float3(.082, .087, .096);
    float3 line = float3(.27, .28, .30);
    float d = 1000.;
{rects}
    if (d < 0.) {{ col = well; a = 1.; }}
    float l = 1. - smoothstep(.04, .16, abs(d));
    col = mix(col, line, l);
    a = max(a, l);
    return half4(half3(col * a), half(a));
}}
"""


def spectrum_display(analyser_ref, x_range, y_range=(-42.0, 18.0)):
    """Native display with only the spectrum and axes; the unit's shader draws its curves on top."""
    def stack():
        return v("Object", obj(1803, "stack_panel_item_layout_settings", {"width#6217": v("Byte", 1), "height#6218": v("Byte", 1)}))
    common = lambda: {"layout_settings#6226": stack(), "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True)}
    spectrum = obj(1852, "display_spectrum_panel_item", {**common(), "analyzer_component#6574": analyser_ref,
                   "graph_style#6575": v("Byte", 1), "color#6577": v("Byte", 0), "tilt_spectrum#11093": v("Double", 4.5)})
    axes = obj(1805, "display_axes_panel_item", {**common(), "show_x_axis#6888": v("Bool", True), "show_y_axis#6889": v("Bool", True),
               "clip_x_axis_lines#6890": v("Bool", False), "clip_y_axis_lines#6891": v("Bool", False),
               "show_x_axis_label#6516": v("Bool", True), "show_y_axis_label#6517": v("Bool", False),
               "show_info_on_hover#6714": v("Bool", True)})
    return obj(1804, "display_panel_item", {**common(), "items#6221": v("ObjectList", owned(spectrum, axes)),
               "brightness#6245": v("Byte", 3), "x_min#6504": v("Double", x_range[0]), "x_max#6505": v("Double", x_range[1]),
               "x_domain#6506": v("Byte", 2), "x_unit#6507": v("Byte", 4), "y_min#6508": v("Double", y_range[0]),
               "y_max#6509": v("Double", y_range[1]), "y_domain#6510": v("Byte", 1), "y_unit#6511": v("Byte", 2),
               "left_margin_visible#10289": v("Bool", False), "right_margin_visible#10290": v("Bool", False),
               "top_margin_visible#10291": v("Bool", False), "bottom_margin_visible#10292": v("Bool", False)})


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

    g = geometry(spec)
    input_proxy = proxy()
    input_owner = connection()
    input_owner["Object"]["fields"]["source_component#248"] = v("Object", input_proxy)
    audio_source = obj(2000, "audio_source_atom", {
        "settings#6194": settings([input_owner]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "port_color#10378": v("Int16", 999),
        "name#3639": v("String", "In"), "preset_identifier#3640": v("String", "IN")})
    compensation = obj(1371, "delay_compensation_atom", {
        "settings#6194": settings([wire(input_proxy)]), "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0)})
    decs = [parameter(d[0], d[1], d[2], d[3], d[4], d[5]) for d in spec["decimals"]]
    for d, atom in zip(spec["decimals"], decs):
        if d[1] in spec.get("log_params", ()):
            atom["fields"]["value_type#702"]["value"]["fields"]["domain#294"] = v("Byte", spec.get("log_domain", 1))
    chs = [indexed_parameter(c[0], c[1], c[2], c[3]) for c in spec["choices"]]
    tgs = [boolean_parameter(t[0], t[1], t[2]) for t in spec.get("toggles", [])]
    n_dec = len(decs)
    inputs = [nitro_port("in", 0, 2, output=False)]
    inputs += [nitro_port(d[7], 1 + i, 1, output=False) for i, d in enumerate(spec["decimals"])]
    inputs += [value_port(c[5], 1 + n_dec + i, boolean=False) for i, c in enumerate(spec["choices"])]
    inputs += [value_port(t[4], 1 + n_dec + len(chs) + i, boolean=True) for i, t in enumerate(spec.get("toggles", []))]
    vectors = spec.get("vectors", 1)
    outputs = [nitro_port("out", 0, 2, output=True)] + [nitro_port("display" if i == 0 else f"display{i + 1}", 1 + i, 4, output=True) for i in range(vectors)]
    if spec.get("native_display") in ("eq", "spectrum"):
        outputs.append(nitro_port("tap", 1 + vectors, 2, output=True))   # the output lifted 34 dB, for the spectrum display
    dsp = obj(1721, "nitro_atom", {
        "settings#6194": settings([wire(compensation), *(wire(p) for p in decs), *(wire(c) for c in chs), *(wire(t) for t in tgs)]),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(*outputs))})
    native_eq = spec.get("native_display") == "eq"
    native = spec.get("native_display") in ("eq", "spectrum")
    drawing_inputs = [wire(dsp, 1 + i) for i in range(vectors)] + [connection() for _ in range(9 - vectors)]
    drawing = obj(5512, "", {
        "settings#6194": settings(drawing_inputs),
        "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
        "prevent_parent_from_sleeping#11002": v("Bool", False),
        "preset_identifier#701": v("String", "PANEL_DRAWING"), "#16316": v("WideString", shader)})
    analyser = None
    display_item, expressions = None, ()
    if native:
        analyser = obj(1851, "spectrum_analyser_component", {
            "settings#6194": settings([wire(dsp, 1 + vectors)]), "channel_count#607": v("Byte", 0), "name#374": v("String", "Output"),
            "prevent_parent_from_sleeping#11002": v("Bool", False), "oversampling#13595": v("Byte", 0),
            "overlap#6571": v("Double", 0.5), "window_function#6573": v("Byte", 12)})
        if native_eq:
            display_item, raw = eq_display(ref(analyser), ref)
            expressions = [obj(1728, "panel_expression", {"expression#6274": v("String", e), "panel_item#6275": ref(t),
                               "attribute_id#6316": v("Int16", a)}) for e, t, a in raw]
        else:
            display_item = spectrum_display(ref(analyser), spec["native_x"])
    in_vu = vu_meter([wire(compensation)]) if spec["meters"].get("in") else None
    out_vu = vu_meter([wire(dsp, 0)]) if spec["meters"].get("out") else None
    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(dsp, 0)])
    disp_h = spec.get("display_h", PANEL_HEIGHT - 2 * TOP)
    frames = [(g["disp_x"] - .2, TOP - .2, g["disp_x"] + g["dw"] + .2, TOP + disp_h + .2)]
    if spec.get("layout") == "bar":
        frames.append((g["side_x"] - .5, TOP - .2, g["width"] - 1.5, PANEL_HEIGHT - TOP + .2))
    else:
        frames.append((g["knob_x"] - .5, TOP - .2, g["width"] - 1.5, PANEL_HEIGHT - TOP + .2))
    shader_src = backdrop_shader(g["width"], frames)
    backdrop = obj(5512, "", {
        "settings#6194": settings([connection() for _ in range(9)]),
        "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
        "prevent_parent_from_sleeping#11002": v("Bool", False),
        "preset_identifier#701": v("String", "BACKDROP"), "#16316": v("WideString", shader_src)})
    def overlay(rects):
        items, exprs = [], []
        for kx, ky, kw, kh, dec in rects:
            its, rules = knob_overlay((kx, ky, kw, kh), (kw / 2.0, CAP_CY), CAP_R, dec[1], dec[2], dec[3])
            items += its
            exprs += [obj(1728, "panel_expression", {"expression#6274": v("String", e), "panel_item#6275": ref(t),
                       "attribute_id#6316": v("Int16", 6309)}) for e, t in rules]
        return items, exprs
    panel = main_panel(spec, g, [ref(p) for p in decs], [ref(c) for c in chs], ref(drawing) if drawing else None,
                       ref(in_vu) if in_vu else None, ref(out_vu) if out_vu else None, display_item, expressions, ref(backdrop), overlay, [ref(t) for t in tgs])
    identity = project["identity"]
    children = [backdrop, audio_source, compensation, *decs, *chs, *tgs, dsp] + ([drawing] if drawing else []) + ([analyser] if analyser else []) + [m for m in (in_vu, out_vu) if m]
    body = obj(151, "device_contents", {
        "child_components#173": v("ObjectList", owned(*children)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_in_ports#177": v("ObjectList", [ref(input_proxy, list_entry=True), *owned(proxy(note=True))]),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", project["presentation"]["description"]),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", False), "suggest_for_audio_input#4847": v("Bool", True),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", spec.get("revision", 7)), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", spec["keywords"]),
        "device_type#391": v("Byte", 0), "has_been_modified#392": v("Bool", True),
        "color_tint#13354": v("Color", [0.0, 0.0, 0.0, 0.0])})
    object_ids = {id(item): index for index, item in enumerate(iter_owned_objects(body), 1)}
    for wrapper, key, target in bindings:
        wrapper[key] = object_ids[id(target)]
    revision = hashlib.sha1(f"{identity['uuid']}/v{spec.get('revision', 7)}".encode("utf-8")).hexdigest()
    return {"header": {"format_version": 3, "serialization_format": 2, "document_version": 207,
                       "object_offset": 0, "resources_offset": 0, "flags": 0},
            "metadata": metadata(project, revision), "body": body, "meta_nonce": "0" * 32, "body_nonce": "0" * 32}
