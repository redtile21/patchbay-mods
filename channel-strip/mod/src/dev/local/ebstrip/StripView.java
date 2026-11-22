package dev.local.ebstrip;

import bitwig.obf.aEv;
import bitwig.obf.aEp;
import bitwig.obf.dUr;
import bitwig.obf.dXL;
import bitwig.obf.dpU;
import bitwig.obf.dqN;
import bitwig.obf.dxF;
import com.bitwig.base.geom.ijY;
import bitwig.obf.drf;
import bitwig.obf.dvv;
import bitwig.obf.dwF;
import com.bitwig.base.geom.mLC;
import com.bitwig.flt.app.Hvv;
import com.bitwig.flt.app.gEH;
import com.bitwig.flt.document.core.iface.bMt;
import com.bitwig.flt.document.core.master.device.k3K;
import com.bitwig.flt.widget.core.device.UTA;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * The strip's expanded view: a Bitwig dialog (dockable like The Grid's expanded view) showing Bitwig's own device
 * chain widget for each slot that has a unit loaded. Modelled on All Lanes View (shaboogen), written in 6.1.7 names.
 */
final class StripView extends dvv implements aEp {
    private final bMt track;
    private final Supplier<List<k3K>> loaded;
    private final dXL column;
    private final dwF filler;
    private final List<k3K> shown = new ArrayList<>();
    private final List<dwF> rows = new ArrayList<>();
    private boolean disposed;

    StripView(bMt track, Supplier<List<k3K>> loaded) {
        super();
        this.track = track;
        this.loaded = loaded;
        XhI(); // set the dialog up (zqN)
        column = new dXL();
        column.MgQ(mLC.Gef); // vertical
        column.H_();
        column.byf(0); // no gap
        filler = column.ocs(); // stretchable space after the last row
        dUr scroll = dUr.Gef(column);
        BBg(scroll); // the content (IwV)
        af(false); // vpw
        dvk(true); // disposed when closed (Grk)
        H_();
        refresh();
    }

    /** Rebuilds the rows when the set of loaded chains changed. */
    void refresh() {
        if (disposed) return;
        try {
            List<k3K> now = loaded.get();
            if (now.equals(shown)) return;
            for (dwF row : rows) {
                column.neH(row); // remove
                row.iy_(); // dispose
            }
            rows.clear();
            column.neH(filler);
            for (k3K chain : now) {
                UTA widget = UTA.MgQ((bitwig.obf.v1Y) chain); // the chain, as the device panel shows it
                rows.add(widget);
                column.IvP(widget);
            }
            column.IvP(filler);
            shown.clear();
            shown.addAll(now);
        } catch (Throwable t) {
            Strip.MOD.log("could not update the expanded view", t);
        }
    }

    void queueRefresh() {
        drf.EO().runAtEndOfCurrentEvent(this::refresh);
    }

    // --- Bitwig's dockable-dialog interface ---

    @Override
    public bMt Anf() {
        return track;
    }

    @Override
    public void iy_() {
        if (!disposed) {
            disposed = true;
            StripViews.disposed(this);
        }
        super.iy_();
    }

    private static long cachedW, cachedH;

    /** Measures the rows (only possible once they are on screen) and remembers the widest. */
    void measure() {
        try {
            long w = 0, h = 0;
            for (dwF row : rows) {
                ijY size = row.iH_();
                w = Math.max(w, size.Gef);
                h += size.sCA;
            }
            if (w > 0) {
                cachedW = Math.max(cachedW, w);
                cachedH = h;
                Strip.MOD.log("measured widest=" + w + " height=" + h);
            }
        } catch (Throwable t) {
            Strip.MOD.log("measure failed: " + t);
        }
    }

    /** The window opens as wide as the widest unit panel seen so far. */
    @Override
    public dxF ly_() {
        if (cachedW > 0) {
            // layout units are device pixels (2 per screen point on a retina display); window sizes are points
            long scale = 2;
            return new dqN(cachedW / scale + 60, Math.min(cachedH / scale + 60, 900));
        }
        return super.ly_();
    }

    boolean isShown() {
        return vTn();
    }

    void close() {
        sCA();
    }

    /** Opens the view in its own window (anchor null) or docked from the anchor widget. */
    void open(dwF anchor) {
        Strip.MOD.log("opening view, rows=" + rows.size());
        gEH app = (gEH) Hvv.mEL();
        dpU where = anchor == null ? aEv.beI : app.beI(anchor, this);
        dwF owner = anchor != null ? anchor : app.LRq();
        beI(owner, where);
    }
}
