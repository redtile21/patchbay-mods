package dev.local.savenewversion;

import bitwig.obf.aCG; // an open project (document)
import bitwig.obf.aDs; // the project window: the widget a shortcut runs in; it knows its current project
import bitwig.obf.dwF; // a window or widget Bitwig uses as the parent of dialogs
import bml.api.Bml;
import com.bitwig.flt.app.Hvv; // the application's file handling: Save, Save As, Open
import com.bitwig.flt.app.gEH; // its implementation, which has the save to a given file
import com.bitwig.flt.document.core.iface.bMt; // a project's document model

import java.io.File;

/** Project: Save New Version. The code behind the "Save New Version" action. */
public final class SaveNewVersion {
    private static final Bml.Mod MOD = Bml.mod("save-new-version");

    private SaveNewVersion() {}

    static int naming() { return MOD.settings().getInt("naming", 0); } // 0 number, 1 date and time
    static void setNaming(int n) { MOD.settings().putInt("naming", n); }

    /** Saves the active project as the next version of its file; a never-saved project gets Bitwig's Save As. */
    static void saveNewVersion(Object widget) {
        try {
            Hvv hvv = Hvv.mEL(); // the application's file handling
            // The project of the window the action ran in, as Bitwig's own Save takes it; else the active one.
            aCG project = widget instanceof aDs window ? window.DYQ() : hvv.bvF();
            if (project == null || !(hvv instanceof gEH app)) {
                MOD.log("no project to save (widget " + (widget == null ? "null" : widget.getClass().getName()) + ")");
                return;
            }
            bMt document = project.Anf(); // the project's document
            String path = document.iEE(); // its file path; empty until first saved
            if (path == null || path.isEmpty()) {
                // Never saved: Bitwig's normal save asks where to put it.
                app.beI(project, false, false, widget instanceof dwF parent ? parent : null, null);
                return;
            }
            File next = VersionName.next(new File(path), naming() == 1);
            app.beI(project, next, false, false, null); // Bitwig's save to a file; the project continues under it
        } catch (Throwable t) {
            MOD.log("save new version failed", t);
        }
    }
}
