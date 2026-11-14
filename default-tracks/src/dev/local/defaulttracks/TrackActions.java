package dev.local.defaulttracks;

import bml.actions.ActionProvider;
import bml.actions.Actions;
import bml.actions.Menu;

/** The mod's actions: a shortcut and Commander entry each, plus the track right-click menu. */
public final class TrackActions implements ActionProvider {
    @Override
    public void declare(Actions actions) {
        actions.category("default_tracks", "Default Tracks");
        for (Kind kind : Kind.values()) {
            if (!kind.exposed) continue;
            actions.action("default_tracks_new_" + kind.id, "New Default " + kind.label + " Track")
                   .category("default_tracks")
                   .in(Menu.selection("track"))
                   .onRun(context -> DefaultTracks.create(kind, context.widget(), context.selection()));
        }
        actions.action("default_tracks_choose_folder", "Choose Default Track Preset Folder...")
               .category("default_tracks")
               .onRun(context -> FolderChooser.choose());
    }
}
