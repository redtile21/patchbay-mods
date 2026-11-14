package dev.local.savenewversion;

import bml.preferences.Page;
import bml.preferences.PreferenceProvider;
import bml.preferences.Preferences;
import bml.preferences.Section;

/** The mod's controls on the shared Mods page of Bitwig's Settings. */
public final class VersionSettings implements PreferenceProvider {
    @Override
    public void declare(Preferences preferences) {
        Page mods = preferences.page("mods", "Mods");
        Section mine = preferences.section(mods, "save_new_version", "Save New Version");
        preferences.choice("naming", "Version suffix", "Number", "Date and time")
                   .in(mine).value(SaveNewVersion::naming, SaveNewVersion::setNaming);
    }
}
