# EB Strip Spike (Spike B)

Sources only (builder files adapted from the blueprint stay in the separate checkout; see `../../DESIGN.md` §8).

Structure, learned by decoding polarity's Multiband FX-4: a chain slot is a `nested_device_chain_slot` (class 587)
with two inputs (audio from a `processing_delay_placeholder_component`, class 1437, and the note proxy). Its
audio output (port 0) feeds the next placeholder, so six slots in series is just a longer wire. A
`component_display_panel_item` (class 1704) per slot shows the chain in the device panel. Multiband FX-4 also
has a `boolean_value_atom` (class 87), the template needed for toggle parameters (Mono, bypass).
