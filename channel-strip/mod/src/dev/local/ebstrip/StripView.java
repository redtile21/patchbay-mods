package dev.local.ebstrip;

import bitwig.obf.aEv;
import bitwig.obf.aEp;
import bitwig.obf.dUr;
import bitwig.obf.dXL;
import bitwig.obf.doI;
import bitwig.obf.doV;
import bitwig.obf.dwC;
import bitwig.obf.dpU;
import bitwig.obf.dqN;
import bitwig.obf.dxE;
import bitwig.obf.dxF;
import bitwig.obf.dxG;
import bitwig.obf.dqO;
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
    private final Supplier<List<Entry>> loaded;
    private final dXL column;
    private final dwF filler;
    private final List<Entry> shown = new ArrayList<>();
    private final List<dwF> rows = new ArrayList<>();
    private boolean disposed;

    StripView(bMt track, Supplier<List<Entry>> loaded) {
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
            List<Entry> now = loaded.get();
            if (now.equals(shown)) return;
            for (dwF row : rows) {
                column.neH(row); // remove
                row.iy_(); // dispose
            }
            rows.clear();
            column.neH(filler);
            for (Entry entry : now) {
                dwF row = row(entry);
                rows.add(row);
                column.IvP(row);
            }
            column.IvP(filler);
            shown.clear();
            shown.addAll(now);
        } catch (Throwable t) {
            Strip.MOD.log("could not update the expanded view", t);
        }
    }

    /** A slot's chain and the name shown in its header. */
    record Entry(k3K chain, String label) {
    }

    /** One slot: a vertical name header at the left, Bitwig's own chain widget beside it. */
    private static dwF row(Entry entry) {
        dwC name = dwC.IKw(); // a vertical label, reading bottom to top
        try {
            // the string is an expression, so a literal is quoted
            com.bitwig.ramona.core.EO prop = (com.bitwig.ramona.core.EO) (Object) name.vws();
            try {
                doI.beI(prop, "\"" + entry.label() + "\"");
            } catch (Throwable first) {
                doI.beI(prop, "'" + entry.label() + "'");
            }
        } catch (Throwable t) {
            Strip.MOD.log("could not label a row", t);
        }
        doV header = doV.beI(name, 1, 1, 5, 5);
        UTA widget = UTA.MgQ((bitwig.obf.v1Y) entry.chain()); // the chain, as the device panel shows it
        dXL row = new dXL();
        row.MgQ(mLC.beI); // horizontal
        row.beI(header, 0.0f);
        row.beI(widget, 1.0f);
        return row;
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
            }
        } catch (Throwable t) {
            Strip.MOD.log("measure failed: " + t);
        }
    }

    /** The window opens as wide as the widest unit panel seen so far. */
    @Override
    public dxF ly_() {
        try {
            var st = Strip.MOD.settings();
            if (st.get("window.width", null) != null) return new dqN(st.getInt("window.width", 800), st.getInt("window.height", 600));
        } catch (Throwable t) {
            Strip.MOD.log("could not read the window size", t);
        }
        if (cachedW > 0) {
            // layout units are device pixels (2 per screen point on a retina display); window sizes are points
            long scale = 2;
            return new dqN(cachedW / scale + 60, Math.min(cachedH / scale + 60, 900));
        }
        return super.ly_();
    }

    /** Where the window opens: where it was last left. */
    @Override
    public dxE lx_() {
        try {
            var st = Strip.MOD.settings();
            if (st.get("window.x", null) != null) return new dqO(st.getInt("window.x", 0), st.getInt("window.y", 0));
        } catch (Throwable t) {
            Strip.MOD.log("could not read the window place", t);
        }
        return super.lx_();
    }

    @Override
    public void beI(dxG move) { // moved
        super.beI(move);
        try {
            Strip.MOD.settings().putInt("window.x", (int) move.um());
            Strip.MOD.settings().putInt("window.y", (int) move.KLw());
        } catch (Throwable t) {
            Strip.MOD.log("could not store the window place", t);
        }
    }

    @Override
    public void Gef(dxG resize) { // resized
        super.Gef(resize);
        try {
            Strip.MOD.settings().putInt("window.width", (int) resize.iAR());
            Strip.MOD.settings().putInt("window.height", (int) resize.gPa());
        } catch (Throwable t) {
            Strip.MOD.log("could not store the window size", t);
        }
    }

    boolean isShown() {
        return vTn();
    }

    void close() {
        sCA();
    }

    /** Opens the view in its own window (anchor null) or docked from the anchor widget. */
    void open(dwF anchor) {
        gEH app = (gEH) Hvv.mEL();
        dpU where = anchor == null ? aEv.beI : app.beI(anchor, this);
        dwF owner = anchor != null ? anchor : app.LRq();
        beI(owner, where);
    }
}
