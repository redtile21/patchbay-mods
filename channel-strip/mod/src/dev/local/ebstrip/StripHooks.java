package dev.local.ebstrip;

import bitwig.obf.cbF;
import bitwig.obf.kh;
import bitwig.obf.lpr;
import bml.api.Arg;
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

    @Hook(target = cbF.class, method = "ymo(Z)V", at = At.BEFORE_RETURN, id = "button-ymo")
    public static void buttonymo(@This cbF atom) {
        try {
            Strip.buttonSet(atom, "ymo");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }


    @Hook(target = kh.class, method = "ZRB(D)V", at = At.BEFORE_RETURN, id = "knob-a")
    public static void knoba(@This kh atom) {
        try {
            Strip.knobSet(atom, "ZRB");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = kh.class, method = "wLf(D)V", at = At.BEFORE_RETURN, id = "knob-b")
    public static void knobb(@This kh atom) {
        try {
            Strip.knobSet(atom, "wLf");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = kh.class, method = "GwM(D)V", at = At.BEFORE_RETURN, id = "knob-c")
    public static void knobc(@This kh atom) {
        try {
            Strip.knobSet(atom, "GwM");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = kh.class, method = "d_(D)V", at = At.BEFORE_RETURN, id = "knob-d")
    public static void knobd(@This kh atom) {
        try {
            Strip.knobSet(atom, "d_");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = kh.class, method = "e_(D)V", at = At.BEFORE_RETURN, id = "knob-e")
    public static void knobe(@This kh atom) {
        try {
            Strip.knobSet(atom, "e_");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = kh.class, method = "mEL(D)V", at = At.BEFORE_RETURN, id = "knob-f")
    public static void knobf(@This kh atom) {
        try {
            Strip.knobSet(atom, "mEL");
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }


    // The device header's window button calls this on the device's model to open or close its window.
    @Hook(target = com.bitwig.flt.document.core.master.device.JHy.class, method = "MgQ(Z)V", at = At.BEFORE_RETURN, id = "device-window")
    public static void deviceWindow(@This com.bitwig.flt.document.core.master.device.JHy device) {
        try {
            Strip.windowSet(device, device.jTT());
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }

    @Hook(target = com.bitwig.flt.document.core.master.device.vP2.class,
          method = "Gef(Lcom/bitwig/flt/document/core/master/device/sgH;I)V", at = At.ENTRY, id = "device-added")
    public static void deviceAdded(@Arg(0) Object device) {
        try {
            Strip.deviceAdded(device);
        } catch (Throwable t) {
            // never let the watcher reach Bitwig's code
        }
    }
}
