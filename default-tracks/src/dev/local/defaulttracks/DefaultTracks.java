package dev.local.defaulttracks;

import bitwig.obf.PiT;
import bitwig.obf.YCD;
import bitwig.obf.aCG;
import bitwig.obf.aDs;
import bitwig.obf.dwF;
import bitwig.obf.dwe;
import bml.api.Bml;
import bml.notifications.Notifications;
import com.bitwig.flt.document.core.iface.bMt;
import com.bitwig.flt.document.core.iface.uVN;
import com.bitwig.flt.document.core.master.CmH;
import com.bitwig.flt.document.core.master.GJy;
import com.bitwig.flt.document.core.master.device.k3K;
import com.bitwig.flt.document.core.master.device.utt;
import com.bitwig.flt.packaging.core.SJF;
import com.bitwig.flt.packaging.core.odK;

import java.io.File;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.List;

/** Creates a track after the selected one and loads the user's Chain preset into it. */
public final class DefaultTracks {
    static final Bml.Mod MOD = Bml.mod("default-tracks");

    private DefaultTracks() {}

    static void create(Kind kind, Object widget, Object menuSelection) {
        try {
            File preset = PresetFinder.find(kind.presetName);
            if (preset == null) {
                MOD.log("preset '" + kind.presetName + "' not found under " + PresetFinder.searchRoot());
                Notifications.toast("Default Tracks: no \"" + kind.presetName + "\" preset found in " + PresetFinder.searchRoot().getName());
                return;
            }
            dwe window = findWindow(widget);
            aCG project = window instanceof aDs projectWindow ? projectWindow.DYQ() : null;
            if (project == null) {
                MOD.log("no project (widget " + (widget == null ? "null" : widget.getClass().getName()) + ")");
                return;
            }
            bMt document = project.Anf();
            uVN root = document.vNR().GwM();
            if (!(root instanceof GJy rootTracks)) {
                MOD.log("unexpected track container " + root.getClass().getName());
                return;
            }
            Place place = placeAfterSelection(root, menuSelection, window);
            uVN container = place.container();
            int index = place.index();
            CmH changes = rootTracks.cc_();
            YCD track;
            utt chain;
            changes.beI("New Default " + kind.label + " Track", false);
            try {
                track = container.beI(kind.type);
                if (kind.instrumentDefaults) track.beI(document.dvk());
                container.beI(track, index, true, null);
                chain = insertChain(track);
            } finally {
                changes.beI(false);
            }
            chain.beI(preset);
            MOD.log("created " + kind.label + " track at " + index + " with " + preset);
        } catch (Throwable t) {
            MOD.log("creating a " + kind + " track failed", t);
            Notifications.toast("Default Tracks: could not create the track (see the log)");
        }
    }

    /** Where the new track goes: a container (the project or a group) and a position in it. */
    private record Place(uVN container, int index) {}

    /**
     * Right after the selected track, in the group that holds it. A selected group gets the track at the end
     * of its own tracks. With nothing selected, the end of the project.
     */
    private static Place placeAfterSelection(uVN root, Object menuSelection, dwe window) {
        List<Object> sources = new ArrayList<>();
        sources.add(menuSelection);
        sources.add(windowSelection(window));
        for (Object source : sources) {
            List<Object> tracks = TrackSelection.tracksIn(source);
            if (tracks.isEmpty()) continue;
            Object selected = tracks.get(tracks.size() - 1);
            if (selected instanceof GJy group) {
                MOD.log("selected a group; adding inside it");
                return new Place(group, group.qaW());
            }
            Place found = locate(root, selected, 0);
            if (found != null) return new Place(found.container(), found.index() + 1);
            MOD.log("selected track " + selected.getClass().getName() + " is not in the track tree");
        }
        StringBuilder kinds = new StringBuilder();
        for (Object child : root.xDy()) kinds.append(' ').append(child.getClass().getSimpleName());
        MOD.log("no selected track found; project children:" + kinds);
        return new Place(root, root.qaW());
    }

    /** The container that directly holds the track, with the track's position in it. */
    private static Place locate(uVN container, Object track, int depth) {
        List<?> children = container.xDy();
        for (int i = 0; i < children.size(); i++) {
            if (same(children.get(i), track)) return new Place(container, i);
        }
        if (depth > 6) return null;
        for (Object child : children) {
            if (child instanceof uVN sub) {
                Place found = locate(sub, track, depth + 1);
                if (found != null) return found;
            }
        }
        return null;
    }

    private static boolean same(Object a, Object b) {
        if (a == b || a.equals(b)) return true;
        return a instanceof PiT x && b instanceof PiT y && x.cb_() != null && x.cb_().equals(y.cb_());
    }

    /** The project window: the widget itself, or (for a menu click on some inner widget) the active window. */
    private static dwe findWindow(Object widget) {
        if (widget instanceof aDs window) return window;
        try {
            if (widget instanceof dwF clicked && clicked.jg_() instanceof aDs owner) return owner;
        } catch (Throwable t) {
            MOD.log("no owning window: " + t);
        }
        try {
            for (Field f : dwe.class.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers()) && dwe.class.isAssignableFrom(f.getType())) {
                    f.setAccessible(true);
                    if (f.get(null) instanceof aDs window) return window;
                }
            }
        } catch (Throwable t) {
            MOD.log("no active window: " + t);
        }
        return null;
    }

    /** What Bitwig's debug tooling calls the window's selection. */
    private static Object windowSelection(dwe window) {
        if (window == null) return null;
        for (Class<?> c = window.getClass(); c != null; c = c.getSuperclass()) {
            try {
                Method m = c.getDeclaredMethod("scr");
                m.setAccessible(true);
                return m.invoke(window);
            } catch (NoSuchMethodException next) {
                // look in the superclass
            } catch (Throwable t) {
                MOD.log("window selection failed: " + t);
                return null;
            }
        }
        MOD.log("no window selection method");
        return null;
    }

    /** Puts a Chain device at the end of the track's devices, as Bitwig's own insert-device tool does. */
    private static utt insertChain(YCD track) throws Exception {
        odK device = null;
        for (Object candidate : SJF.beI()) {
            if (((odK) candidate).Gef().equalsIgnoreCase("Chain")) { device = (odK) candidate; break; }
        }
        if (device == null) throw new IllegalStateException("no Chain device");
        utt chain = utt.Bqk(device.beI());
        k3K devices = ((PiT) track).YQe();
        devices.Gef(chain, devices.XnJ(), false, null);
        return chain;
    }
}
