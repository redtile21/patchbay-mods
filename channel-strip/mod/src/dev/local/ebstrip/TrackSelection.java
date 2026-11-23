package dev.local.ebstrip;

import bitwig.obf.YCD;
import com.bitwig.flt.document.core.master.GJy;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * Finds the tracks inside whatever Bitwig hands over as "the selection". The selection object's class is
 * Bitwig's own, so this looks for tracks without naming it, and logs what it saw to make a miss easy to diagnose.
 */
final class TrackSelection {
    private TrackSelection() {}

    static List<Object> tracksIn(Object selection) {
        List<Object> found = new ArrayList<>();
        if (selection == null) return found;
        collect(selection, found, 0);
        if (found.isEmpty()) describe(selection);
        return found;
    }

    private static void collect(Object o, List<Object> out, int depth) {
        if (o == null || depth > 3) return;
        if (o instanceof YCD || o instanceof GJy) {   // a track, or a group (which holds tracks of its own)
            if (!out.contains(o)) out.add(o);
            return;
        }
        if (o instanceof Collection<?> items) {
            for (Object item : items) collect(item, out, depth + 1);
            return;
        }
        if (o instanceof Object[] items) {
            for (Object item : items) collect(item, out, depth + 1);
            return;
        }
        if (depth > 1 || o instanceof CharSequence || o instanceof Number || o instanceof Boolean || o.getClass().isEnum()) return;
        for (Class<?> c = o.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers()) || !holdsTracks(f.getType())) continue;
                try {
                    f.setAccessible(true);
                    collect(f.get(o), out, depth + 1);
                } catch (Throwable ignored) {
                    // not readable: try the next member
                }
            }
            for (Method m : c.getDeclaredMethods()) {
                if (Modifier.isStatic(m.getModifiers()) || m.getParameterCount() != 0 || !holdsTracks(m.getReturnType())) continue;
                try {
                    m.setAccessible(true);
                    collect(m.invoke(o), out, depth + 1);
                } catch (Throwable ignored) {
                    // not callable: try the next member
                }
            }
        }
    }

    /** Logs the shape of a selection object we could not read, so the next version can. */
    private static void describe(Object o) {
        StringBuilder sb = new StringBuilder("selection shape:");
        for (Class<?> c = o.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            sb.append("\n  ").append(c.getName());
            for (Field f : c.getDeclaredFields()) {
                if (!Modifier.isStatic(f.getModifiers())) sb.append("\n    field ").append(f.getType().getName()).append(' ').append(f.getName());
            }
            for (Method m : c.getDeclaredMethods()) {
                if (!Modifier.isStatic(m.getModifiers()) && m.getParameterCount() == 0 && !m.getReturnType().isPrimitive()) {
                    sb.append("\n    method ").append(m.getReturnType().getName()).append(' ').append(m.getName()).append("()");
                }
            }
        }
        Strip.MOD.log(sb.toString());
    }

    private static boolean holdsTracks(Class<?> type) {
        return YCD.class.isAssignableFrom(type) || GJy.class.isAssignableFrom(type) || Collection.class.isAssignableFrom(type)
                || (type.isArray() && !type.getComponentType().isPrimitive());
    }
}
