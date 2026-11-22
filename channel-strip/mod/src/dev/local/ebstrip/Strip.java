package dev.local.ebstrip;

import bitwig.obf.drf;
import bitwig.obf.PiT;
import bitwig.obf.aCG;
import bitwig.obf.aDs;
import bitwig.obf.dwF;
import bitwig.obf.dwe;
import bitwig.obf.lpr;
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

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Spike: find EB strip devices on the selected track, list their nested chains, insert a unit into the first one. */
final class Strip {
    static final Bml.Mod MOD = Bml.mod("eb-strip-console");
    /** The strip and the nested-chain test strip. */
    static final Set<String> STRIP_UUIDS = Set.of("4f1e9a37-0b6c-4d82-95e3-d7a2c8b1f406", "5d0c6a52-3c5e-4f0b-9a58-2f1d4b7e6c31");

    private Strip() {}

    private record Ctx(aCG project, GJy root, PiT track) {}

    private record Hit(Object object, String path) {}

    /** What the Probe action does: logs the devices on the selected track and the nested chains inside each. */
    static void probe(Object widget, Object selection) {
        try {
            Ctx c = context(widget, selection);
            if (c == null) return;
            Map<UUID, String> names = registry();
            StringBuilder out = new StringBuilder("probe: track " + c.track.getClass().getName());
            List<Hit> devices = walk(c.track.YQe(), utt.class, 6, 5000);
            out.append("\n  devices on the track: ").append(devices.size());
            int strips = 0;
            for (Hit d : devices) {
                utt device = (utt) d.object;
                UUID id = device.beI();
                out.append("\n  device ").append(names.getOrDefault(id, "?")).append(' ').append(id).append("  at ").append(d.path);
                if (!STRIP_UUIDS.contains(String.valueOf(id))) continue;
                strips++;
                out.append("\n    identifiers:").append(scanIdentifiers(device));
                List<Hit> chains = slotChains(device);
                out.append("\n    nested chains: ").append(chains.size());
                for (Hit chain : chains) {
                    k3K k = (k3K) chain.object;
                    out.append("\n      chain count=").append(k.XnJ()).append("  at ").append(chain.path);
                    for (Hit inner : walk(k, utt.class, 4, 2000)) {
                        UUID innerId = ((utt) inner.object).beI();
                        out.append("\n        holds ").append(names.getOrDefault(innerId, "?")).append(' ').append(innerId);
                    }
                }
            }
            MOD.log(out.toString());
            Notifications.toast("EB Strip probe: " + devices.size() + " device(s), " + strips + " strip(s). See the Patchbay log.");
        } catch (Throwable t) {
            MOD.log("probe failed", t);
            Notifications.toast("EB Strip probe failed (see the log)");
        }
    }

    /** Inserts the named unit device at the end of the first nested chain of the first strip on the selected track. */
    static void insertIntoSlot(int slot, String unitName, Object widget, Object selection) {
        try {
            Ctx c = context(widget, selection);
            if (c == null) return;
            odK unit = null;
            for (Object candidate : SJF.beI()) {
                if (((odK) candidate).Gef().equalsIgnoreCase(unitName)) { unit = (odK) candidate; break; }
            }
            if (unit == null) {
                MOD.log("no registered device named " + unitName + "; registered: " + registry().values());
                Notifications.toast("EB Strip: device '" + unitName + "' is not registered (see the log)");
                return;
            }
            utt strip = findStrip(c);
            if (strip == null) {
                Notifications.toast("EB Strip: no strip on the selected track");
                return;
            }
            Hit found = slotChain(strip, slot);
            if (found == null) {
                MOD.log("slot " + slot + " chain not found");
                Notifications.toast("EB Strip: slot " + slot + " not found (see the log)");
                return;
            }
            k3K chain = (k3K) found.object;
            utt device = utt.byf(unit.beI());
            CmH changes = c.root.cc_();
            changes.beI("Insert " + unitName + " in slot " + slot, false);
            try {
                chain.Gef(device, chain.qJX().size(), false, null);
            } finally {
                changes.beI(false);
            }
            StripViews.refreshAll();
            MOD.log("inserted " + unitName + " into slot " + slot + " at " + found.path);
            Notifications.toast("EB Strip: inserted " + unitName + " into slot " + slot);
        } catch (Throwable t) {
            MOD.log("insert failed", t);
            Notifications.toast("EB Strip: insert failed (see the log)");
        }
    }

    /** Reports objects whose String fields match a strip identifier (SLOTn_TYPE, SLOTn_CHAIN), with their readable members. */
    private static String scanIdentifiers(utt strip) {
        StringBuilder out = new StringBuilder();
        Map<Object, Boolean> seen = new IdentityHashMap<>();
        List<Hit> level = new ArrayList<>();
        level.add(new Hit(strip, ""));
        seen.put(strip, true);
        int nodes = 0, reported = 0;
        for (int depth = 0; depth <= 9 && !level.isEmpty() && nodes < 40000 && reported < 40; depth++) {
            List<Hit> next = new ArrayList<>();
            for (Hit hit : level) {
                if (++nodes > 40000) break;
                Object o = hit.object;
                if (o != strip && o instanceof utt) continue;
                String id = identifierOf(o);
                if (id != null && reported < 40) {
                    reported++;
                    out.append("\n    ").append(id).append("  ").append(o.getClass().getName()).append("  at ").append(hit.path).append(describe(o));
                }
                for (Hit child : children(hit)) {
                    if (child.object == null || seen.put(child.object, true) != null) continue;
                    next.add(child);
                }
            }
            level = next;
        }
        return out.toString();
    }

    private static String identifierOf(Object o) {
        String name = o.getClass().getName();
        if (name.contains(".") && !name.startsWith("com.bitwig.")) return null;
        for (Class<?> c = o.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers()) || f.getType() != String.class) continue;
                try {
                    f.setAccessible(true);
                    Object v = f.get(o);
                    if (v instanceof String text && text.matches("SLOT[1-6]_(TYPE|CHAIN)|INPUT_GAIN")) return text;
                } catch (Throwable ignored) {
                    // unreadable
                }
            }
        }
        return null;
    }

    /** Primitive and String fields, and simple no-argument getters, so the next version knows where a value lives. */
    private static String describe(Object o) {
        StringBuilder out = new StringBuilder();
        for (Class<?> c = o.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers())) continue;
                Class<?> t = f.getType();
                if (!(t.isPrimitive() || t == String.class)) continue;
                try {
                    f.setAccessible(true);
                    out.append("\n        ").append(c.getSimpleName()).append('.').append(f.getName()).append(" = ").append(f.get(o));
                } catch (Throwable ignored) {
                    // unreadable
                }
            }
            for (Method m : c.getDeclaredMethods()) {
                if (Modifier.isStatic(m.getModifiers()) || m.getParameterCount() != 0) continue;
                Class<?> t = m.getReturnType();
                if (!(t == int.class || t == double.class || t == float.class || t == boolean.class || t == String.class || t == byte.class)) continue;
                try {
                    m.setAccessible(true);
                    out.append("\n        ").append(c.getSimpleName()).append('.').append(m.getName()).append("() = ").append(m.invoke(o));
                } catch (Throwable ignored) {
                    // not callable
                }
            }
        }
        return out.toString();
    }

    /** The nested chain of slot n (1-6): found by the slot's own identifier, because the chain list has no fixed order. */
    private static Hit slotChain(utt strip, int n) {
        String wanted = "SLOT" + n + "_CHAIN";
        Map<Object, Boolean> seen = new IdentityHashMap<>();
        List<Hit> level = new ArrayList<>();
        level.add(new Hit(strip, ""));
        seen.put(strip, true);
        int nodes = 0;
        for (int depth = 0; depth <= 9 && !level.isEmpty() && nodes < 40000; depth++) {
            List<Hit> next = new ArrayList<>();
            for (Hit hit : level) {
                if (++nodes > 40000) break;
                Object o = hit.object;
                if (o != strip && o instanceof utt) continue;
                if (wanted.equals(identifierOf(o))) {
                    List<Hit> chains = walk(o, k3K.class, 4, 500);
                    if (!chains.isEmpty()) return new Hit(chains.get(0).object, hit.path + chains.get(0).path);
                }
                for (Hit child : children(hit)) {
                    if (child.object == null || seen.put(child.object, true) != null) continue;
                    next.add(child);
                }
            }
            level = next;
        }
        return null;
    }

    private static utt findStrip(Ctx c) {
        for (Hit d : walk(c.track.YQe(), utt.class, 6, 5000)) {
            if (STRIP_UUIDS.contains(String.valueOf(((utt) d.object).beI()))) return (utt) d.object;
        }
        return null;
    }

    /** The strip's own nested chains: the walk also reaches the chain the strip sits in, which holds the strip itself. */
    private static List<Hit> slotChains(utt strip) {
        List<Hit> chains = new ArrayList<>();
        for (Hit hit : walk(strip, k3K.class, 8, 20000)) {
            boolean parent = false;
            for (Hit inner : walk(hit.object, utt.class, 2, 500)) {
                if (inner.object == strip) { parent = true; break; }
            }
            if (!parent) chains.add(hit);
        }
        return chains;
    }

    /** Removes every device from slot n's chain (one undo step). */
    static void clearSlot(int slot, Object widget, Object selection) {
        try {
            Ctx c = context(widget, selection);
            if (c == null) return;
            utt strip = findStrip(c);
            if (strip == null) { Notifications.toast("EB Strip: no strip on the selected track"); return; }
            Hit found = slotChain(strip, slot);
            if (found == null) { Notifications.toast("EB Strip: slot " + slot + " not found"); return; }
            k3K chain = (k3K) found.object;
            List<Object> devices = new ArrayList<>();
            for (Object d : new ArrayList<>(chain.qJX())) if (d instanceof utt) devices.add(d);
            if (devices.isEmpty()) { Notifications.toast("EB Strip: slot " + slot + " is already empty"); return; }
            CmH changes = c.root.cc_();
            changes.beI("Clear strip slot " + slot, false);
            try {
                for (Object d : devices) {
                    if (!chain.qJX().contains(d)) continue;
                    chain.MgQ((utt) d);
                }
            } finally {
                changes.beI(false);
            }
            StripViews.refreshAll();
            MOD.log("cleared " + devices.size() + " device(s) from slot " + slot);
            Notifications.toast("EB Strip: cleared slot " + slot);
        } catch (Throwable t) {
            MOD.log("clear failed", t);
            Notifications.toast("EB Strip: clear failed (see the log)");
        }
    }

    // ---- Watcher: keeps each slot's loaded unit in step with the strip's SLOTn_TYPE dropdown ----

    private static final class Watch {
        final Ctx c; final utt strip;
        final lpr[] types = new lpr[7];
        final k3K[] chains = new k3K[7];
        Watch(Ctx c, utt strip) { this.c = c; this.strip = strip; }
    }

    private static final List<Watch> WATCHES = new ArrayList<>();
    private static final ThreadLocal<Boolean> BUSY = ThreadLocal.withInitial(() -> false);

    /** Starts keeping the first strip on the selected track in step with its dropdowns. */
    static void arm(Object widget, Object selection) {
        try {
            Ctx c = context(widget, selection);
            if (c == null) return;
            utt strip = findStrip(c);
            if (strip == null) { Notifications.toast("EB Strip: no strip on the selected track"); return; }
            Watch w = new Watch(c, strip);
            for (int n = 1; n <= 6; n++) {
                Object atom = findByIdentifier(strip, "SLOT" + n + "_TYPE");
                Hit chain = slotChain(strip, n);
                if (!(atom instanceof lpr) || chain == null) {
                    MOD.log("watch: slot " + n + " is missing its dropdown or chain");
                    Notifications.toast("EB Strip: this strip has no slot dropdowns (see the log)");
                    return;
                }
                w.types[n] = (lpr) atom;
                w.chains[n] = (k3K) chain.object;
            }
            synchronized (WATCHES) {
                WATCHES.removeIf(o -> o.strip == strip);
                WATCHES.add(w);
            }
            MOD.log("watching strip on the selected track");
            Notifications.toast("EB Strip: watching the dropdowns on this track");
            onChangesEnded();
        } catch (Throwable t) {
            MOD.log("watch failed", t);
        }
    }

    /** Opens the strip's expanded view (its own window): Bitwig's chain widget for each slot with a unit loaded. */
    static void openView(Object widget, Object selection) {
        try {
            arm(widget, selection);
            Ctx c = context(widget, selection);
            if (c == null) return;
            utt strip = findStrip(c);
            Watch watch = null;
            synchronized (WATCHES) {
                for (Watch w : WATCHES) if (w.strip == strip) watch = w;
            }
            if (watch == null) return;
            final Watch w = watch;
            java.util.function.Supplier<List<k3K>> loaded = () -> {
                List<k3K> out = new ArrayList<>();
                for (int n = 1; n <= 6; n++) if (!w.chains[n].qJX().isEmpty()) out.add(w.chains[n]);
                return out;
            };
            StripView view = new StripView((com.bitwig.flt.document.core.iface.bMt) c.root.cc_(), loaded);
            StripViews.closeAll();
            StripViews.add(view);
            drf.EO().runAtEndOfCurrentEvent(() -> {
                try {
                    view.open(null);
                    drf.EO().runAtEndOfCurrentEvent(view::measure);
                } catch (Throwable t) {
                    MOD.log("open view failed", t);
                }
            });
        } catch (Throwable t) {
            MOD.log("open view failed", t);
            Notifications.toast("EB Strip: could not open the expanded view (see the log)");
        }
    }

    private static Object findByIdentifier(utt strip, String wanted) {
        Map<Object, Boolean> seen = new IdentityHashMap<>();
        List<Hit> level = new ArrayList<>();
        level.add(new Hit(strip, ""));
        seen.put(strip, true);
        int nodes = 0;
        for (int depth = 0; depth <= 9 && !level.isEmpty() && nodes < 40000; depth++) {
            List<Hit> next = new ArrayList<>();
            for (Hit hit : level) {
                if (++nodes > 40000) break;
                Object o = hit.object;
                if (o != strip && o instanceof utt) continue;
                if (wanted.equals(identifierOf(o))) return o;
                for (Hit child : children(hit)) {
                    if (child.object == null || seen.put(child.object, true) != null) continue;
                    next.add(child);
                }
            }
            level = next;
        }
        return null;
    }

    /** Called by the hook each time Bitwig finishes an undoable change. */
    /** Called after a dropdown atom's value is set: brings that strip's slots in line if the atom is one we watch. */
    static void valueSet(lpr atom) {
        boolean ours = false;
        synchronized (WATCHES) {
            for (Watch w : WATCHES) for (int n = 1; n <= 6; n++) if (w.types[n] == atom) ours = true;
        }
        if (!ours && !AUTO_FAILED.contains(atom)) ours = autoArm(atom);
        if (ours) onChangesEnded();
    }

    private static final Set<Object> AUTO_FAILED = Collections.newSetFromMap(new java.util.WeakHashMap<>());

    /** Finds the strip that owns this dropdown by following Bitwig's own references upwards, and starts watching it. */
    private static boolean autoArm(lpr atom) {
        try {
            String id = identifierOf(atom);
            if (id == null || !id.matches("SLOT[1-6]_TYPE")) return false;
            utt strip = (utt) findUp(atom, o -> o instanceof utt u && STRIP_UUIDS.contains(String.valueOf(u.beI())), 8, 6000);
            PiT track = strip == null ? null : (PiT) findUp(strip, o -> o instanceof PiT, 8, 6000);
            GJy root = track == null ? null : (GJy) findUp(track, o -> o instanceof GJy, 8, 6000);
            if (strip == null || track == null || root == null) {
                MOD.log("auto-arm: strip=" + (strip != null) + " track=" + (track != null) + " root=" + (root != null));
                AUTO_FAILED.add(atom);
                return false;
            }
            Watch w = new Watch(new Ctx(null, root, track), strip);
            for (int n = 1; n <= 6; n++) {
                Object a = findByIdentifier(strip, "SLOT" + n + "_TYPE");
                Hit chain = slotChain(strip, n);
                if (!(a instanceof lpr) || chain == null) { AUTO_FAILED.add(atom); MOD.log("auto-arm: slot " + n + " incomplete"); return false; }
                w.types[n] = (lpr) a;
                w.chains[n] = (k3K) chain.object;
            }
            synchronized (WATCHES) {
                WATCHES.removeIf(o -> o.strip == strip);
                WATCHES.add(w);
            }
            MOD.log("auto-armed strip");
            return true;
        } catch (Throwable t) {
            AUTO_FAILED.add(atom);
            MOD.log("auto-arm failed", t);
            return false;
        }
    }

    /** Breadth-first search along Bitwig's references, in any direction, for the first object the test accepts. */
    private static Object findUp(Object start, java.util.function.Predicate<Object> test, int maxDepth, int maxNodes) {
        Map<Object, Boolean> seen = new IdentityHashMap<>();
        List<Hit> level = new ArrayList<>();
        level.add(new Hit(start, ""));
        seen.put(start, true);
        int nodes = 0;
        for (int depth = 0; depth <= maxDepth && !level.isEmpty() && nodes < maxNodes; depth++) {
            List<Hit> next = new ArrayList<>();
            for (Hit hit : level) {
                if (++nodes > maxNodes) break;
                if (hit.object != start && test.test(hit.object)) return hit.object;
                for (Hit child : children(hit, true)) {
                    if (child.object == null || seen.put(child.object, true) != null) continue;
                    next.add(child);
                }
            }
            level = next;
        }
        return null;
    }

    private static int hookCalls;

    static void onChangesEnded() {
        if (hookCalls < 40) { hookCalls++; MOD.log("changes ended #" + hookCalls + " watches=" + WATCHES.size() + " busy=" + BUSY.get()); }
        if (WATCHES.isEmpty() || BUSY.get()) return;
        BUSY.set(true);
        try {
            List<Watch> copy;
            synchronized (WATCHES) { copy = new ArrayList<>(WATCHES); }
            Map<UUID, String> names = null;
            for (Watch w : copy) {
                try {
                    for (int n = 1; n <= 6; n++) {
                        String want = w.types[n].sSO();
                        List<?> devices = new ArrayList<>(w.chains[n].qJX());
                        String have = "Bypass";
                        if (!devices.isEmpty()) {
                            if (names == null) names = registry();
                            have = names.getOrDefault(((utt) devices.get(0)).beI(), "?");
                        }
                        if (hookCalls < 40) MOD.log("slot " + n + " want=" + want + " have=" + have);
                        String wantDevice = "Bypass".equals(want) ? "Bypass" : "EB " + want;
                        if (wantDevice.equalsIgnoreCase(have)) continue;
                        swap(w, n, devices, wantDevice);
                    }
                } catch (Throwable t) {
                    MOD.log("watch dropped (strip gone or changed)", t);
                    synchronized (WATCHES) { WATCHES.remove(w); }
                }
            }
        } finally {
            BUSY.set(false);
        }
    }

    private static void swap(Watch w, int n, List<?> devices, String wantDevice) {
        odK unit = null;
        if (!"Bypass".equals(wantDevice)) {
            for (Object candidate : SJF.beI()) {
                if (((odK) candidate).Gef().equalsIgnoreCase(wantDevice)) { unit = (odK) candidate; break; }
            }
            if (unit == null) { MOD.log("swap: no registered device " + wantDevice); return; }
        }
        k3K chain = w.chains[n];
        CmH changes = w.c.root.cc_();
        changes.beI("Slot " + n + ": " + wantDevice, false);
        try {
            for (Object d : devices) if (chain.qJX().contains(d)) chain.MgQ((utt) d);
            if (unit != null) chain.Gef(utt.byf(unit.beI()), chain.qJX().size(), false, null);
        } finally {
            changes.beI(false);
        }
        MOD.log("slot " + n + " now " + wantDevice);
        StripViews.refreshAll();
    }

    private static Map<UUID, String> registry() {
        Map<UUID, String> names = new LinkedHashMap<>();
        for (Object candidate : SJF.beI()) {
            odK entry = (odK) candidate;
            names.put(entry.beI(), entry.Gef());
        }
        return names;
    }

    /**
     * Breadth-first walk through Bitwig's own objects, reporting every instance of {@code type} below the root. It does not
     * look inside a reported object, and keeps out of tracks, containers and the project so it cannot wander upwards.
     */
    private static List<Hit> walk(Object root, Class<?> type, int maxDepth, int maxNodes) {
        List<Hit> found = new ArrayList<>();
        Map<Object, Boolean> seen = new IdentityHashMap<>();
        List<Hit> level = new ArrayList<>();
        level.add(new Hit(root, ""));
        seen.put(root, true);
        int nodes = 0;
        for (int depth = 0; depth <= maxDepth && !level.isEmpty() && nodes < maxNodes; depth++) {
            List<Hit> next = new ArrayList<>();
            for (Hit hit : level) {
                if (++nodes > maxNodes) break;
                Object o = hit.object;
                if (o != root && type.isInstance(o)) { found.add(hit); continue; }
                for (Hit child : children(hit)) {
                    if (child.object == null || seen.put(child.object, true) != null) continue;
                    next.add(child);
                }
            }
            level = next;
        }
        return found;
    }

    private static List<Hit> children(Hit hit) { return children(hit, false); }

    private static List<Hit> children(Hit hit, boolean unrestricted) {
        List<Hit> out = new ArrayList<>();
        Object o = hit.object;
        if (o instanceof Collection<?> items) {
            int i = 0;
            for (Object item : items) out.add(new Hit(item, hit.path + "[" + i++ + "]"));
            return out;
        }
        if (o instanceof Map<?, ?> map) {
            for (Map.Entry<?, ?> e : map.entrySet()) out.add(new Hit(e.getValue(), hit.path + "{" + e.getKey() + "}"));
            return out;
        }
        if (o instanceof Object[] items) {
            for (int i = 0; i < items.length; i++) out.add(new Hit(items[i], hit.path + "[" + i + "]"));
            return out;
        }
        String name = o.getClass().getName();
        if (name.contains(".") && !name.startsWith("com.bitwig.")) return out;
        if (!unrestricted && (o instanceof PiT || o instanceof GJy || o instanceof uVN || o instanceof aCG || o instanceof bMt || o instanceof dwe)) {
            if (!hit.path.isEmpty()) return out;
        }
        for (Class<?> c = o.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers()) || f.getType().isPrimitive() || f.getType() == String.class) continue;
                try {
                    f.setAccessible(true);
                    Object value = f.get(o);
                    if (value != null) out.add(new Hit(value, hit.path + "." + f.getName()));
                } catch (Throwable ignored) {
                    // unreadable: skip
                }
            }
        }
        return out;
    }

    private static Ctx context(Object widget, Object menuSelection) {
        dwe window = findWindow(widget);
        aCG project = window instanceof aDs projectWindow ? projectWindow.DYQ() : null;
        if (project == null) {
            MOD.log("no project");
            Notifications.toast("EB Strip: no project");
            return null;
        }
        uVN root = project.Anf().vNR().GwM();
        if (!(root instanceof GJy rootTracks)) {
            MOD.log("unexpected track container " + root.getClass().getName());
            return null;
        }
        List<Object> sources = new ArrayList<>();
        sources.add(menuSelection);
        sources.add(windowSelection(window));
        for (Object source : sources) {
            List<Object> tracks = TrackSelection.tracksIn(source);
            for (Object t : tracks) {
                if (t instanceof PiT track) return new Ctx(project, rootTracks, track);
            }
        }
        Notifications.toast("EB Strip: select a track first");
        return null;
    }

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
        return null;
    }
}
