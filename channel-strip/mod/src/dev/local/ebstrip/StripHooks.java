package dev.local.ebstrip;

import bitwig.obf.cbF;
import bitwig.obf.lpr;
import bml.api.At;
import bml.api.Hook;
import bml.api.This;

/** Runs the strip watcher once a dropdown's value has been set. */
public final class StripHooks {
    @Hook(target = lpr.class, method = "MgQ(I)V", at = At.BEFORE_RETURN, id = "dropdown-set")
    public static void dropdownSet(@This lpr atom) {
        try {
            Strip.valueSet(atom);
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = cbF.class, method = "MgQ(Z)V", at = At.BEFORE_RETURN, id = "button-MgQ")
    public static void buttonMgQ(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "MgQ");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = cbF.class, method = "BBg(Z)V", at = At.BEFORE_RETURN, id = "button-BBg")
    public static void buttonBBg(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "BBg");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = cbF.class, method = "byf(Z)V", at = At.BEFORE_RETURN, id = "button-byf")
    public static void buttonbyf(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "byf");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = cbF.class, method = "Bqk(Z)V", at = At.BEFORE_RETURN, id = "button-Bqk")
    public static void buttonBqk(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "Bqk");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = cbF.class, method = "ymo(Z)V", at = At.BEFORE_RETURN, id = "button-ymo")
    public static void buttonymo(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "ymo");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = cbF.class, method = "SQL(Z)V", at = At.BEFORE_RETURN, id = "button-SQL")
    public static void buttonSQL(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "SQL");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }
}
