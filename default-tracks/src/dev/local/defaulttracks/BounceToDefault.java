package dev.local.defaulttracks;

import bitwig.obf.PiT;
import bitwig.obf.aCG;
import bitwig.obf.aDs;
import bitwig.obf.dog;
import bitwig.obf.dom;
import bitwig.obf.drf;
import bitwig.obf.dwF;
import bitwig.obf.dwe;
import bml.notifications.Notifications;
import com.bitwig.flt.document.core.iface.uVN;

import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;
import java.util.TimerTask;

/**
 * Runs Bitwig's own Bounce command, then gives the track it creates (right after the source track, same group
 * and color) the default audio chain.
 */
final class BounceToDefault {
    private static final long POLL_MS = 400;
    private static final int MAX_POLLS = 150; // about a minute

    private BounceToDefault() {}

    static void run(Object widget) {
        try {
            File preset = PresetFinder.find(Kind.AUDIO.presetName);
            if (preset == null) {
                DefaultTracks.MOD.log("preset '" + Kind.AUDIO.presetName + "' not found under " + PresetFinder.searchRoot());
                Notifications.toast("Default Tracks: no \"" + Kind.AUDIO.presetName + "\" preset found in " + PresetFinder.searchRoot().getName());
                return;
            }
            dwe window = DefaultTracks.findWindowFor(widget);
            if (!(window instanceof aDs projectWindow)) { DefaultTracks.MOD.log("bounce: no project window"); return; }
            aCG project = projectWindow.DYQ();
            uVN root = project.Anf().vNR().GwM();
            dom action = drf.EO().mEL("bounce");
            dog binding = action == null || !(widget instanceof dwF clicked) ? null : clicked.MgQ(action);
            if (binding == null) {
                DefaultTracks.MOD.log("bounce: no Bounce binding here (action " + action + ", widget "
                        + (widget == null ? "null" : widget.getClass().getName()) + ")");
                Notifications.toast("Default Tracks: use this from a clip's right-click menu (not a shortcut)");
                return;
            }
            Set<Object> before = Collections.newSetFromMap(new IdentityHashMap<>());
            collect(root, before, null);
            binding.run();
            DefaultTracks.MOD.log("bounce: started");
            watch(root, before, preset);
        } catch (Throwable t) {
            DefaultTracks.MOD.log("bounce to default track failed", t);
            Notifications.toast("Default Tracks: could not bounce (see the log)");
        }
    }

    /** Polls on Bitwig's event queue until the bounce has made its track, then gives it the chain. */
    private static void watch(uVN root, Set<Object> before, File preset) {
        TimerTask[] self = new TimerTask[1];
        int[] polls = {0};
        self[0] = drf.EO().beI(() -> {
            try {
                List<PiT> fresh = new ArrayList<>();
                collect(root, null, fresh);
                fresh.removeIf(before::contains);
                if (!fresh.isEmpty()) {
                    self[0].cancel();
                    DefaultTracks.giveDefaultChain(root, fresh, preset);
                } else if (++polls[0] >= MAX_POLLS) {
                    self[0].cancel();
                    DefaultTracks.MOD.log("bounce: no new track appeared");
                }
            } catch (Throwable t) {
                self[0].cancel();
                DefaultTracks.MOD.log("bounce watch failed", t);
            }
        }, POLL_MS, POLL_MS);
    }

    private static void collect(uVN container, Set<Object> all, List<PiT> tracks) {
        for (Object child : container.xDy()) {
            if (all != null) all.add(child);
            if (tracks != null && child instanceof PiT track) tracks.add(track);
            if (child instanceof uVN sub) collect(sub, all, tracks);
        }
    }
}
