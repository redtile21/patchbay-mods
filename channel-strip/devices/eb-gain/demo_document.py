"""EB Gain document, adapted from the Blueprint Gain builder (three decimal parameters)."""
from __future__ import annotations

import hashlib

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v

PANEL_WIDTH, PANEL_HEIGHT = 72, 53

# name, identifier, min, max, default, digits
PARAMS = (
    ("Gain", "GAIN", -24.0, 24.0, 0.0, 1),
    ("Pan", "PAN", -100.0, 100.0, 0.0, 0),
    ("Width", "WIDTH", 0.0, 200.0, 100.0, 0),
)
KNOBS = (("Gain", "Output gain in dB"), ("Pan", "Constant-power pan"), ("Width", "Stereo width, 100 is unchanged"))


def owned(*objects):
    return [{"Object": item} for item in objects]


def settings(connections=()):
    desktop = obj(17, "desktop_settings", {
        "x#17": v("Int16", 0), "y#18": v("Int16", 0),
        "color#19": v("Color", [0.5, 0.5, 0.5, 1.0]),
    })
    return v("Object", obj(236, "component_settings", {
        "desktop_settings#612": v("Object", desktop),
        "inport_connections#614": v("ObjectList", list(connections)),
        "is_polyphonic#615": v("Bool", False),
    }))


def proxy(*, output=False, note=False):
    caption = " Note out" if note else " Audio in (PARENT)" if output else " Audio out (PARENT)"
    port_fields = {
        "name#498": v("String", ""), "description#4741": v("String", ""),
        "decorated_name#499": v("String", caption), "is_inport#500": v("Bool", output),
        "is_optional#1384": v("Bool", False), "exclude_from_graph#7174": v("Bool", False),
    }
    if note:
        port_fields["oversampling#13326"] = v("Byte", 0)
        port = obj(61, "note_port", port_fields)
    else:
        port_fields.update({"channel_count#372": v("Byte", 3), "oversampling#13324": v("Int32", 0)})
        port = obj(242, "audio_port", port_fields)
    return obj(50 if output else 154, "proxy_out_port_component" if output else "proxy_in_port_component", {
        "settings#6194": settings(), "port#301": v("Object", port),
    })


def parameter(name, identifier, minimum, maximum, default, digits):
    value_type = obj(123, "decimal_value_type", {
        "min#292": v("Double", minimum), "max#293": v("Double", maximum),
        "default_value#891": v("Double", default), "domain#294": v("Byte", 0),
        "engine_domain#295": v("Byte", 0), "value_origin#3014": v("Byte", 2 if minimum < 0 < maximum else 0),
        "pixel_step_size#1988": v("Double", -1.0), "unit#296": v("Byte", 0),
        "#297": v("Byte", digits), "parameter_smoothing#4433": v("Bool", True),
        "allow_automation_curves#4434": v("Bool", True),
    })
    return obj(289, "decimal_value_atom", {
        "settings#6194": settings(), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "name#374": v("String", name),
        "short_name#821": v("String", name), "preset_identifier#701": v("String", identifier),
        "modulations_to_ignore#3826": v("String", ""),
        "value_type#702": v("Object", value_type), "value#712": v("Double", default),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
    })


def indexed_parameter(name, identifier, items, default):
    item_objs = [{"Object": obj(258, "indexed_value_item", {
        "id#650": v("Byte", i), "name#651": v("String", label), "icon#9823": v("String", ""),
        "description#9824": v("String", ""), "deprecated#10795": v("Bool", False),
    })} for i, label in enumerate(items)]
    value_type = obj(155, "indexed_value_type", {
        "items#393": v("ObjectList", item_objs), "default_value#6958": v("Byte", default),
        "is_periodic#16667": v("Bool", False),
    })
    return obj(180, "indexed_value_atom", {
        "settings#6194": settings(), "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "preset_identifier#701": v("String", identifier), "name#374": v("String", name),
        "short_name#821": v("String", name), "should_inherit_name#10561": v("Bool", False),
        "modulations_to_ignore#3826": v("String", ""), "value_type#702": v("Object", value_type),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
        "value#457": v("Byte", default),
    })


def boolean_parameter(name, identifier, default):
    value_type = obj(198, "boolean_value_type", {
        "icon_name#4755": v("String", ""), "default_value#6957": v("Bool", default),
    })
    return obj(87, "boolean_value_atom", {
        "settings#6194": settings(), "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "preset_identifier#701": v("String", identifier), "name#374": v("String", name),
        "short_name#821": v("String", name), "should_inherit_name#10561": v("Bool", False),
        "modulations_to_ignore#3826": v("String", ""), "value_type#702": v("Object", value_type),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
        "value#210": v("Bool", default),
    })


def value_port(name, index, *, boolean):
    return obj(2428, "nitro_port_info", {
        "name#8557": v("String", name), "desc#8558": v("String", ""),
        "channel_count#8559": v("Byte", 0 if boolean else 1), "index#8560": v("Byte", index),
        "kind#8561": v("Byte", 3), "is_input#8562": v("Bool", True),
        "is_double_precision#10071": v("Bool", False), "is_compressed_mask#8563": v("Int32", 16777215),
        "is_compressable#8564": v("Bool", False), "event_size#8565": v("Byte", 1 if boolean else 0),
        "event_type#8566": v("String", "i1" if boolean else ""),
    })


def nitro_port(name, index, channels, *, output):
    return obj(2428, "nitro_port_info", {
        "name#8557": v("String", name), "desc#8558": v("String", ""),
        "channel_count#8559": v("Byte", channels), "index#8560": v("Byte", index),
        "kind#8561": v("Byte", 1), "is_input#8562": v("Bool", not output),
        "is_double_precision#10071": v("Bool", False), "is_compressed_mask#8563": v("Int32", 16777215),
        "is_compressable#8564": v("Bool", False), "event_size#8565": v("Byte", 0),
        "event_type#8566": v("String", ""),
    })


def main_panel(knob_bindings, drawing_binding, choice_binding, toggle_binding):
    meter = obj(5517, "", {
        "layout_settings#6226": v("Object", grid_layout(4, 36, 64, 14)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
        "help_location#10546": v("Byte", 0), "data_model#6220": drawing_binding,
    })
    knobs = []
    for (title, tip), binding, x in zip(KNOBS, knob_bindings, (4, 26, 48)):
        knobs.append(obj(1687, "knob_panel_item", {
            "layout_settings#6226": v("Object", grid_layout(x, 4, 21, 22)),
            "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
            "tooltip_text#6867": v("String", tip),
            "data_model#6220": binding, "title#6241": v("String", title),
            "knob_size#6223": v("Byte", 3), "show_value_popup#10569": v("Bool", True),
            "attribute_id#11012": v("Int16", 712), "knob_style#7055": v("Byte", 3),
            "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", 6),
        }))
    chooser = obj(1714, "popup_chooser_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(4, 28, 30, 5)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", "Polarity invert"), "data_model#6220": choice_binding,
        "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", 0),
        "style#6266": v("Byte", 7), "color#7528": v("Int16", 6),
    })
    toggle = obj(1714, "popup_chooser_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(38, 28, 30, 5)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", "Sum to mono"), "data_model#6220": toggle_binding,
        "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", 0),
        "style#6266": v("Byte", 7), "color#7528": v("Int16", 6),
    })
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(meter, *knobs, chooser, toggle)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6),
        "brightness#6245": v("Byte", 0),
    })
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", PANEL_WIDTH), "height#6233": v("Byte", PANEL_HEIGHT),
        "expressions#6277": v("ObjectList", []),
    })


def metadata(project, revision):
    identity = project["identity"]
    fields = {
        "application_version_name": v("String", project["target"]["bitwigVersion"]),
        "creator": v("String", identity["creator"]), "device_creator": v("String", identity["creator"]),
        "device_category": v("String", identity["category"]),
        "device_description": v("String", project["presentation"]["description"]),
        "device_id": v("String", identity["uuid"]), "device_uuid": v("Uuid", identity["uuid"]),
        "device_name": v("String", project["name"]), "device_type": v("String", "audio_to_audio"),
        "has_audio_input": v("Bool", True), "has_audio_output": v("Bool", True),
        "has_note_input": v("Bool", False), "has_note_output": v("Bool", False),
        "preset_name": v("String", project["name"]), "revision_id": v("String", revision),
        "revision_no": v("Int32", 1), "suggest_for_audio_input": v("Bool", True),
        "suggest_for_note_input": v("Bool", False), "tags": v("String", "gain pan width stereo elodea blackstar"),
        "type": v("String", "application/bitwig-device"),
    }
    return {**obj(4, "meta", fields), "wide_names": [False] * len(fields)}


def document(project, binary, shader):
    # Bind to Python objects first. Serialize references only after the tree is final.
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
    params = [parameter(*spec) for spec in PARAMS]
    polarity = indexed_parameter("Polarity", "POLARITY", ("Off", "L", "R", "Both"), 0)
    mono = indexed_parameter("Mono", "MONO", ("Off", "On"), 0)
    dsp = obj(1721, "nitro_atom", {
        "settings#6194": settings([wire(compensation), *(wire(p) for p in params), wire(polarity), wire(mono)]),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0), "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
        # These descriptors follow the inport and outport order in gain.nitro.
        "nitro_inputs#15756": v("ObjectList", owned(
            nitro_port("in", 0, 2, output=False), nitro_port("gain_db", 1, 1, output=False),
            nitro_port("pan", 2, 1, output=False), nitro_port("stereo_width", 3, 1, output=False),
            value_port("polarity", 4, boolean=False), value_port("sum_mono", 5, boolean=False),
        )),
        "nitro_outputs#15757": v("ObjectList", owned(
            nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True),
        )),
    })
    drawing = obj(5512, "", {
        "settings#6194": settings([wire(dsp, 1), *(connection() for _ in range(8))]),
        "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
        "prevent_parent_from_sleeping#11002": v("Bool", False),
        "preset_identifier#701": v("String", "PANEL_DRAWING"), "#16316": v("WideString", shader),
    })
    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(dsp, 0)])
    panel = main_panel([ref(p) for p in params], ref(drawing), ref(polarity), ref(mono))
    identity = project["identity"]
    body = obj(151, "device_contents", {
        "child_components#173": v("ObjectList", owned(audio_source, compensation, *params, polarity, mono, dsp, drawing)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_in_ports#177": v("ObjectList", [ref(input_proxy, list_entry=True), *owned(proxy(note=True))]),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", project["presentation"]["description"]),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", False), "suggest_for_audio_input#4847": v("Bool", True),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", 1), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", "gain pan width stereo elodea blackstar EB"),
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
        "metadata": metadata(project, revision), "body": body,
        "meta_nonce": "0" * 32, "body_nonce": "0" * 32,
    }
