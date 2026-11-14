package dev.local.defaulttracks;

import bml.preferences.Page;
import bml.preferences.PreferenceProvider;
import bml.preferences.Preferences;
import bml.preferences.Section;

/** The mod's controls on the shared Mods page of Bitwig's Settings. */
public final class TrackSettings implements PreferenceProvider {
    @Override
    public void declare(Preferences preferences) {
        Page mods = preferences.page("mods", "Mods");
        Section mine = preferences.section(mods, "default_tracks", "Default Tracks");
        preferences.choice("location", "Preset location", "User library", "Custom folder")
                   .in(mine).value(Settings::location, Settings::setLocation);
    }
}
