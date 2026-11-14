package dev.local.savenewversion;

import bml.actions.ActionProvider;
import bml.actions.Actions;

/** The "Save New Version" action: a shortcut and Commander entry. */
public final class VersionActions implements ActionProvider {
    @Override
    public void declare(Actions actions) {
        actions.category("save_new_version", "Save New Version");
        actions.action("save_new_version_save", "Save New Version")
               .category("save_new_version")
               .onRun(context -> SaveNewVersion.saveNewVersion(context.widget()));
    }
}
