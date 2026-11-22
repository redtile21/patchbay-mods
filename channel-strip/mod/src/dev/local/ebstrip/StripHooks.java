package dev.local.ebstrip;

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
}
