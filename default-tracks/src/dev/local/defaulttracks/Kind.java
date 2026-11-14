package dev.local.defaulttracks;

import bitwig.obf.fV;

/** The kinds of track the mod can create, and the Chain preset each one loads. */
enum Kind {
    INSTRUMENT("instrument", "Instrument", "Default Instrument Track", fV.beI, true, true),
    AUDIO("audio", "Audio", "Default Audio Track", fV.Gef, false, true),
    /** Built and ready, but not registered as an action yet (flip {@code exposed} to turn it on). */
    HYBRID("hybrid", "Hybrid", "Default Hybrid Track", fV.sCA, true, false);

    final String id;
    final String label;
    final String presetName;
    final fV type;
    /** An instrument or hybrid track gets the project's default instrument settings, as Bitwig's own creation does. */
    final boolean instrumentDefaults;
    /** Whether the mod registers an action for this kind. */
    final boolean exposed;

    Kind(String id, String label, String presetName, fV type, boolean instrumentDefaults, boolean exposed) {
        this.id = id;
        this.label = label;
        this.presetName = presetName;
        this.type = type;
        this.instrumentDefaults = instrumentDefaults;
        this.exposed = exposed;
    }
}
