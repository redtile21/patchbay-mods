package dev.local.ebstrip;

import bml.actions.ActionProvider;
import bml.actions.Actions;
import bml.actions.Menu;

/** Track menu action: open the selected track's strip in its expanded view (the strip's View button does the same). */
public final class StripActions implements ActionProvider {
    @Override
    public void declare(Actions actions) {
        actions.category("eb_strip", "EB Strip");
        actions.action("eb_strip_view", "EB Strip: Open Expanded View")
               .category("eb_strip")
               .in(Menu.selection("track"))
               .onRun(context -> Strip.openView(context.widget(), context.selection()));
    }
}
