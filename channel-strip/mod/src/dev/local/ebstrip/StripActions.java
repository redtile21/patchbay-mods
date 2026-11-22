package dev.local.ebstrip;

import bml.actions.ActionProvider;
import bml.actions.Actions;
import bml.actions.Menu;

/** Spike actions: probe the selected track, and insert a unit into the first slot of its strip. */
public final class StripActions implements ActionProvider {
    private static final String[][] UNITS = {
        {"gain", "EB Gain"}, {"eq", "EB EQ"}, {"compressor", "EB Compressor"}, {"saturation", "EB Saturation"}, {"limiter", "EB Limiter"},
    };

    @Override
    public void declare(Actions actions) {
        actions.category("eb_strip", "EB Strip");
        actions.action("eb_strip_probe", "EB Strip: Probe Selected Track")
               .category("eb_strip")
               .in(Menu.selection("track"))
               .onRun(context -> Strip.probe(context.widget(), context.selection()));
        actions.action("eb_strip_watch", "EB Strip: Watch Selected Track")
               .category("eb_strip")
               .in(Menu.selection("track"))
               .onRun(context -> Strip.arm(context.widget(), context.selection()));
        for (int slot = 1; slot <= 3; slot++) {
            final int n = slot;
            actions.action("eb_strip_clear_" + n, "EB Strip: Clear Slot " + n)
                   .category("eb_strip")
                   .in(Menu.selection("track"))
                   .onRun(context -> Strip.clearSlot(n, context.widget(), context.selection()));
            for (String[] unit : UNITS) {
                actions.action("eb_strip_insert_" + unit[0] + "_" + n, "EB Strip: Insert " + unit[1] + " in Slot " + n)
                       .category("eb_strip")
                       .in(Menu.selection("track"))
                       .onRun(context -> Strip.insertIntoSlot(n, unit[1], context.widget(), context.selection()));
            }
        }
    }
}
