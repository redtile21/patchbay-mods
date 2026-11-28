"""Generate eq.nitro: four bands (low shelf/bell, two bells, high shelf/bell) plus high-pass and low-pass.
RBJ cookbook biquads, transposed direct form II. Coefficients are recomputed only when a band's parameters change."""
from pathlib import Path

L = []
def w(s=""): L.append(s)

w("component eb_eq")
w("{")
w("    audio_inport in;")
ports = [("hpf",0.0),("low_gain",0.0),("low_freq",100.0),("low_q",0.71),("lm_gain",0.0),("lm_freq",500.0),("lm_q",1.0),
         ("hm_gain",0.0),("hm_freq",2500.0),("hm_q",1.0),("high_gain",0.0),("high_freq",8000.0),("high_q",0.71),("lpf",100.0)]
for n,d in ports: w(f"    audio_inport f32 {n} = {d};")
w("    value_inport i32 low_shape;")
w("    value_inport i32 high_shape;")
w("    value_inport i32 hp_slope;")
w("    value_inport i32 lp_slope;")
w("    audio_outport out;")
w("    audio_outport f32<4> display;")
w("    audio_outport f32<4> display2;")
w("    audio_outport tap;")
names = ["hp","hp2","lo","lm","hm","hi","lp","lp2"]
for n in names:
    for c in ("b0","b1","b2","a1","a2"): w(f"    f32 {c}_{n} = {'1.0' if c=='b0' else '0.0'};")
    w(f"    f32<2> z1_{n} = 0.0;")
    w(f"    f32<2> z2_{n} = 0.0;")
for n in ("hpf","low_gain","low_freq","low_q","lm_gain","lm_freq","lm_q","hm_gain","hm_freq","hm_q","high_gain","high_freq","high_q","lpf"):
    w(f"    f32 p_{n} = -999.0;")
w("    i32 p_low_shape = -1;")
w("    i32 p_high_shape = -1;")
w("    i32 p_hp_slope = -1;")
w("    i32 p_lp_slope = -1;")
w("    reset")
w("    {")
for n in names: w(f"        z1_{n} = 0.0;\n        z2_{n} = 0.0;")
for n in ("hpf","low_gain","low_freq","low_q","lm_gain","lm_freq","lm_q","hm_gain","hm_freq","hm_q","high_gain","high_freq","high_q","lpf"):
    w(f"        p_{n} = -999.0;")
w("        p_low_shape = -1;\n        p_high_shape = -1;\n        p_hp_slope = -1;\n        p_lp_slope = -1;")
w("    }")
w("    process")
w("    {")
w("        f32<> x = in;")
w("        f32 sr = EC.samplerate;")
def set_coef(n, b0,b1,b2,a0,a1,a2):
    w(f"            f32 ia_{n} = 1.0 / ({a0});")
    w(f"            b0_{n} = ({b0}) * ia_{n};\n            b1_{n} = ({b1}) * ia_{n};\n            b2_{n} = ({b2}) * ia_{n};")
    w(f"            a1_{n} = ({a1}) * ia_{n};\n            a2_{n} = ({a2}) * ia_{n};")

def peak(n, g, f, q):
    w(f"            f32 w0 = 6.283185307 * fmin(fmax({f}, 20.0), 20000.0) / sr;")
    w("            f32 cw = cos(w0);\n            f32 sw = sin(w0);")
    w(f"            f32 A = exp({g} * 0.0575646273);")
    w(f"            f32 al = sw / (2.0 * fmax({q}, 0.1));")
    set_coef(n,"1.0 + al * A","-2.0 * cw","1.0 - al * A","1.0 + al / A","-2.0 * cw","1.0 - al / A")

def shelf(n, g, f, low, q):
    w(f"            f32 w0 = 6.283185307 * fmin(fmax({f}, 20.0), 20000.0) / sr;")
    w("            f32 cw = cos(w0);\n            f32 sw = sin(w0);")
    w(f"            f32 A = exp({g} * 0.0575646273);")
    w("            f32 sA = sqrt(A);")
    w(f"            f32 al2 = sw * sA / fmax({q}, 0.1);")
    if low:
        set_coef(n,"A * ((A + 1.0) - (A - 1.0) * cw + al2)","2.0 * A * ((A - 1.0) - (A + 1.0) * cw)",
                 "A * ((A + 1.0) - (A - 1.0) * cw - al2)","(A + 1.0) + (A - 1.0) * cw + al2",
                 "-2.0 * ((A - 1.0) + (A + 1.0) * cw)","(A + 1.0) + (A - 1.0) * cw - al2")
    else:
        set_coef(n,"A * ((A + 1.0) + (A - 1.0) * cw + al2)","-2.0 * A * ((A - 1.0) + (A + 1.0) * cw)",
                 "A * ((A + 1.0) + (A - 1.0) * cw - al2)","(A + 1.0) - (A - 1.0) * cw + al2",
                 "2.0 * ((A - 1.0) - (A + 1.0) * cw)","(A + 1.0) - (A - 1.0) * cw - al2")

def pass_filter(n, f, high):
    w(f"            f32 w0 = 6.283185307 * fmin(fmax({f}, 20.0), 20000.0) / sr;")
    w("            f32 cw = cos(w0);\n            f32 sw = sin(w0);\n            f32 al = sw * 0.70710678;")
    if high: set_coef(n,"(1.0 + cw) * 0.5","-(1.0 + cw)","(1.0 + cw) * 0.5","1.0 + al","-2.0 * cw","1.0 - al")
    else: set_coef(n,"(1.0 - cw) * 0.5","1.0 - cw","(1.0 - cw) * 0.5","1.0 + al","-2.0 * cw","1.0 - al")

def update(cond, body_fn):
    w(f"        if ({cond})")
    w("        {")
    body_fn()
    w("        }")

def ident(n):
    w(f"            b0_{n} = 1.0;\n            b1_{n} = 0.0;\n            b2_{n} = 0.0;\n            a1_{n} = 0.0;\n            a2_{n} = 0.0;")
def sec(n, high, q):
    w(f"                f32 al_{n} = sw / (2.0 * {q});")
    if high: set_coef(n,"(1.0 + cw) * 0.5","-(1.0 + cw)","(1.0 + cw) * 0.5",f"1.0 + al_{n}","-2.0 * cw",f"1.0 - al_{n}")
    else: set_coef(n,"(1.0 - cw) * 0.5","1.0 - cw","(1.0 - cw) * 0.5",f"1.0 + al_{n}","-2.0 * cw",f"1.0 - al_{n}")
def slope_filter(a, a2, par, slope, high, off_cond):
    w(f"        if ({par} != p_{par} || {slope} != p_{slope})")
    w("        {")
    w(f"            p_{par} = {par};\n            p_{slope} = {slope};")
    ident(a); ident(a2)
    w(f"            if ({off_cond})")
    w("            {")
    w(f"                f32 w0 = 6.283185307 * fmin(fmax(20.0 * exp(0.06907755 * {par}), 20.0), 20000.0) / sr;")
    w("                f32 cw = cos(w0);\n                f32 sw = sin(w0);")
    w(f"                if ({slope} == 0)")
    w("                {")
    w("                    f32 ik = 1.0 / (1.0 + cw);")
    w("                    f32 kk = sw * ik;")
    w(f"                    f32 il = 1.0 / (1.0 + kk);")
    if high:
        w(f"                    b0_{a} = il;\n                    b1_{a} = -il;\n                    a1_{a} = (kk - 1.0) * il;")
    else:
        w(f"                    b0_{a} = kk * il;\n                    b1_{a} = kk * il;\n                    a1_{a} = (kk - 1.0) * il;")
    w("                }")
    w("                else")
    w("                {")
    w("                    f32 q1 = 0.70710678;")
    w(f"                    if ({slope} == 2)")
    w("                    {")
    w("                        q1 = 0.5411961;")
    w("                    }")
    sec(a, high, "q1")
    w(f"                    if ({slope} == 2)")
    w("                    {")
    sec(a2, high, "1.306563")
    w("                    }")
    w("                }")
    w("            }")
    w("        }")
slope_filter("hp","hp2","hpf","hp_slope",True,"hpf > 0.5")
update("low_gain != p_low_gain || low_freq != p_low_freq || low_q != p_low_q || low_shape != p_low_shape",
       lambda: (w("            p_low_gain = low_gain;\n            p_low_freq = low_freq;\n            p_low_q = low_q;\n            p_low_shape = low_shape;"),
                w("            if (low_shape == 0)"), w("            {"), shelf("lo","low_gain","low_freq",True,"low_q"), w("            }"),
                w("            else"), w("            {"), peak("lo","low_gain","low_freq","low_q"), w("            }")))
update("lm_gain != p_lm_gain || lm_freq != p_lm_freq || lm_q != p_lm_q",
       lambda: (w("            p_lm_gain = lm_gain;\n            p_lm_freq = lm_freq;\n            p_lm_q = lm_q;"), peak("lm","lm_gain","lm_freq","lm_q")))
update("hm_gain != p_hm_gain || hm_freq != p_hm_freq || hm_q != p_hm_q",
       lambda: (w("            p_hm_gain = hm_gain;\n            p_hm_freq = hm_freq;\n            p_hm_q = hm_q;"), peak("hm","hm_gain","hm_freq","hm_q")))
update("high_gain != p_high_gain || high_freq != p_high_freq || high_q != p_high_q || high_shape != p_high_shape",
       lambda: (w("            p_high_gain = high_gain;\n            p_high_freq = high_freq;\n            p_high_q = high_q;\n            p_high_shape = high_shape;"),
                w("            if (high_shape == 0)"), w("            {"), shelf("hi","high_gain","high_freq",False,"high_q"), w("            }"),
                w("            else"), w("            {"), peak("hi","high_gain","high_freq","high_q"), w("            }")))
slope_filter("lp","lp2","lpf","lp_slope",False,"lpf < 99.5")

src = "x"
for i, n in enumerate(names):
    w(f"        f32<> y_{n} = b0_{n} * {src} + z1_{n};")
    w(f"        z1_{n} = b1_{n} * {src} - a1_{n} * y_{n} + z2_{n};")
    w(f"        z2_{n} = b2_{n} * {src} - a2_{n} * y_{n};")
    src = f"y_{n}"
w(f"        f32<> y = {src};")
w("        out = y;")
w("        f32<> boosted = y * 50.0;")
w("        tap = boosted;")
w("        f32 sh_lo = 0.0;\n        if (low_shape == 1)\n        {\n            sh_lo = 1.0;\n        }")
w("        f32 sh_hi = 0.0;\n        if (high_shape == 1)\n        {\n            sh_hi = 1.0;\n        }")
def fi(f): return f"floor(fmin(4095.0, fmax(0.0, log10(fmax({f}, 20.0) / 20.0) / 3.0 * 4095.0)) + 0.5)"
def gi(gv): return f"floor(fmin(300.0, fmax(0.0, ({gv} + 15.0) * 10.0)) + 0.5)"
def qi(q): return f"floor(fmin(360.0, fmax(0.0, ({q} - 0.4) * 100.0)) + 0.5)"
w("        f32 scale = 0.00000005960464477539;")
w(f"        f32 c_lo = (sh_lo * 1310720.0 + {gi('low_gain')} * 4096.0 + {fi('low_freq')}) * scale;")
w(f"        f32 c_lm = ({gi('lm_gain')} * 4096.0 + {fi('lm_freq')}) * scale;")
w(f"        f32 c_hm = ({gi('hm_gain')} * 4096.0 + {fi('hm_freq')}) * scale;")
w(f"        f32 c_hi = (sh_hi * 1310720.0 + {gi('high_gain')} * 4096.0 + {fi('high_freq')}) * scale;")
w("        f32 hp_i = 0.0;\n        if (hpf > 0.5)\n        {\n            hp_i = floor(fmin(4095.0, fmax(0.0, hpf * 40.95)) + 0.5);\n        }")
w(f"        f32 c_fl = (hp_i * 4096.0 + floor(fmin(4095.0, fmax(0.0, lpf * 40.95)) + 0.5)) * scale;")
w(f"        f32 c_q = ({qi('lm_q')} * 512.0 + {qi('hm_q')}) * scale;")
w("        display = <c_lo, c_lm, c_hm, c_hi>;")
w(f"        f32 c_qe = ({qi('low_q')} * 512.0 + {qi('high_q')}) * scale;")
w("        f32 hs = 1.0;\n        if (hp_slope == 0)\n        {\n            hs = 0.0;\n        }\n        if (hp_slope == 2)\n        {\n            hs = 2.0;\n        }")
w("        f32 ls = 1.0;\n        if (lp_slope == 0)\n        {\n            ls = 0.0;\n        }\n        if (lp_slope == 2)\n        {\n            ls = 2.0;\n        }")
w("        f32 c_sl = (hs * 4.0 + ls) * scale;")
w("        display2 = <c_fl, c_q, c_qe, c_sl>;")
w("    }")
w("}")
Path(__file__).with_name("eq.nitro").write_text("\n".join(L) + "\n")
