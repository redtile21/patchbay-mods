package dev.local.ebstrip;

import java.util.ArrayList;
import java.util.List;

/** The open expanded views, refreshed whenever a strip's units change. */
final class StripViews {
    private static final List<StripView> OPEN = new ArrayList<>();

    private StripViews() {
    }

    static void add(StripView view) {
        OPEN.add(view);
    }

    static void disposed(StripView view) {
        OPEN.remove(view);
    }

    static boolean hasOpen() {
        return !OPEN.isEmpty();
    }

    /** Disposes every earlier view, shown or not, so a stale one can't swallow the next open. */
    static void closeAll() {
        for (StripView view : new ArrayList<>(OPEN)) {
            try {
                view.close();
                view.iy_();
            } catch (Throwable t) {
                Strip.MOD.log("closing old view", t);
            }
        }
        OPEN.clear();
    }

    static void refreshAll() {
        for (StripView view : new ArrayList<>(OPEN)) view.queueRefresh();
    }
}
