"""Generate panel.sksl for the strip's slot mini displays."""
from pathlib import Path

GLYPHS = {
 "A": [[(.05,1.95),(.5,.05),(.95,1.95)],[(.25,1.3),(.75,1.3)]],
 "C": [[(.95,.45),(.7,.08),(.3,.08),(.05,.45),(.05,1.55),(.3,1.92),(.7,1.92),(.95,1.55)]],
 "D": [[(.08,.05),(.08,1.95),(.55,1.95),(.92,1.5),(.92,.5),(.55,.05),(.08,.05)]],
 "E": [[(.9,.05),(.1,.05),(.1,1.95),(.9,1.95)],[(.1,1.),(.7,1.)]],
 "G": [[(.95,.45),(.7,.08),(.3,.08),(.05,.45),(.05,1.55),(.3,1.92),(.7,1.92),(.95,1.55),(.95,1.05),(.55,1.05)]],
 "H": [[(.1,.05),(.1,1.95)],[(.9,.05),(.9,1.95)],[(.1,1.),(.9,1.)]],
 "I": [[(.5,.05),(.5,1.95)],[(.2,.05),(.8,.05)],[(.2,1.95),(.8,1.95)]],
 "K": [[(.1,.05),(.1,1.95)],[(.9,.05),(.1,1.1)],[(.35,.8),(.9,1.95)]],
 "L": [[(.1,.05),(.1,1.95),(.9,1.95)]],
 "M": [[(.05,1.95),(.05,.05),(.5,1.2),(.95,.05),(.95,1.95)]],
 "N": [[(.1,1.95),(.1,.05),(.9,1.95),(.9,.05)]],
 "O": [[(.3,.05),(.7,.05),(.92,.4),(.92,1.6),(.7,1.95),(.3,1.95),(.08,1.6),(.08,.4),(.3,.05)]],
 "P": [[(.1,1.95),(.1,.05),(.7,.05),(.92,.35),(.92,.8),(.7,1.1),(.1,1.1)]],
 "R": [[(.1,1.95),(.1,.05),(.7,.05),(.92,.35),(.92,.8),(.7,1.1),(.1,1.1)],[(.45,1.1),(.92,1.95)]],
 "S": [[(.9,.35),(.7,.05),(.3,.05),(.08,.35),(.1,.7),(.5,1.),(.9,1.3),(.92,1.65),(.7,1.95),(.3,1.95),(.08,1.65)]],
 "T": [[(.05,.05),(.95,.05)],[(.5,.05),(.5,1.95)]],
 "U": [[(.1,.05),(.1,1.55),(.3,1.95),(.7,1.95),(.9,1.55),(.9,.05)]],
 "V": [[(.05,.05),(.5,1.95),(.95,.05)]],
 "W": [[(.03,.05),(.25,1.95),(.5,.8),(.75,1.95),(.97,.05)]],
 "X": [[(.1,.05),(.9,1.95)],[(.9,.05),(.1,1.95)]],
 "Y": [[(.05,.05),(.5,1.),(.95,.05)],[(.5,1.),(.5,1.95)]],
}

def letter_fn():
    out = ["// Monoline sans-serif capital in a 1 x 2 box; c is 1 for A to 26 for Z, 0 draws nothing.",
           "float letter(float2 q, float c) {", "    if (c < .5) return 0.;", "    float m = 10.;"]
    first = True
    for ch, strokes in GLYPHS.items():
        code = ord(ch) - 64
        out.append(f"    {'if' if first else 'else if'} (c > {code - .5} && c < {code + .5}) {{")
        first = False
        for s in strokes:
            for (a, b) in zip(s, s[1:]):
                out.append(f"        m = min(m, sdseg(q, float2({a[0]}, {a[1]}), float2({b[0]}, {b[1]})));")
        out.append("    }")
    out += ["    return 1. - smoothstep(.10, .20, m);", "}"]
    return "\n".join(out)

def code(w):
    return [str(float(ord(c) - 64)) for c in w] + ["0."] * (6 - len(w))

WORDS = {1: ("GAIN", "PAN", "WIDTH"), 2: ("LOW", "MID", "HIGH"), 3: ("THRESH", "RATIO", "MAKEUP"),
         4: ("DRIVE", "TYPE", "MIX"), 5: ("INPUT", "CEIL", "REL")}

def label_block():
    lines = []
    for k, ws in WORDS.items():
        lines.append(f"        if (kind > {k - .5} && kind < {k + .5}) {{")
        for j, w in enumerate(ws):
            lines.append(f"            lit = max(lit, word(p, {32 + 56 * j}., 109., 8., {', '.join(code(w))}));")
        lines.append("        }")
    return "\n".join(lines)

SEG = Path(__file__).resolve().parents[1].joinpath("eb-unit", "seg.sksl").read_text()
sd = SEG[SEG.index("float sdseg"):SEG.index("// Monoline sans-serif digit")] if "// Monoline sans-serif digit" in SEG else None
assert sd, "seg.sksl layout changed"

SHADER = '''// Mini display for one strip slot.
// audioLow:    kind / 8 (0 bypass, 1 gain, 2 eq, 3 compressor, 4 saturation, 5 limiter), input level, output level (-60..+6 dB), aux
//              (compressor gain reduction / 24 dB, limiter gain reduction / 12 dB)
// audioMedium: the three macro knobs / 100
uniform float4 audioLow;
uniform float4 audioMedium;

''' + sd + letter_fn() + '''

// A word of up to six letters centred on x; the baseline origin is the top-left of the first glyph.
float word(float2 p, float cx, float y, float h, float a, float b, float c, float d, float e, float f) {
    float w = h * .5;
    float adv = w * 1.3;
    float n = 0.;
    if (a > .5) n += 1.;
    if (b > .5) n += 1.;
    if (c > .5) n += 1.;
    if (d > .5) n += 1.;
    if (e > .5) n += 1.;
    if (f > .5) n += 1.;
    float x0 = cx - n * adv * .5;
    float2 s = p - float2(x0, y - h);
    float lit = 0.;
    lit = max(lit, letter(s / w, a));
    lit = max(lit, letter((s - float2(adv, 0.)) / w, b));
    lit = max(lit, letter((s - float2(2. * adv, 0.)) / w, c));
    lit = max(lit, letter((s - float2(3. * adv, 0.)) / w, d));
    lit = max(lit, letter((s - float2(4. * adv, 0.)) / w, e));
    lit = max(lit, letter((s - float2(5. * adv, 0.)) / w, f));
    return lit;
}

float xr(float tw, float f0) {
    return tw / tan(3.1415927 * clamp(f0, 10., 22000.) / 48000.);
}
float peakdb(float g, float f, float q, float tw) {
    float x = xr(tw, f);
    float x2 = x * x;
    float A = pow(10., g / 40.);
    float qq = max(q, .1);
    float u = (1. - x2) * (1. - x2);
    return 10. * log((u + x2 * A * A / (qq * qq)) / (u + x2 / (A * A * qq * qq))) / 2.302585;
}
float shelfdb(float g, float f, float q, float tw, bool low) {
    float x = xr(tw, f);
    float x2 = x * x;
    float A = pow(10., g / 40.);
    float k2 = A / (q * q);
    float n; float d;
    if (low) {
        n = (A - x2) * (A - x2) + x2 * k2;
        d = (1. - A * x2) * (1. - A * x2) + x2 * k2;
    } else {
        n = (1. - A * x2) * (1. - A * x2) + x2 * k2;
        d = (A - x2) * (A - x2) + x2 * k2;
    }
    return 10. * log(A * A * n / d) / 2.302585;
}
float tanhf(float v) {
    float e = exp(2. * clamp(v, -12., 12.));
    return (e - 1.) / (e + 1.);
}
float shape(float v, float kd) {
    if (kd < .5) return tanhf(v);
    if (kd < 1.5) return v >= 0. ? tanhf(v) : tanhf(v * .7) / .7;
    if (kd < 2.5) {
        float c = clamp(v, -1., 1.);
        return 1.5 * c - .5 * c * c * c;
    }
    return clamp(v, -1., 1.);
}
float curvec(float x, float t, float r, float w) {
    float over = x - t;
    float y = x;
    if (2. * over > w) {
        y = t + over / r;
    } else if (2. * over > -w) {
        float k = over + w * .5;
        y = x + (1. / r - 1.) * k * k / (2. * max(w, .0001));
    }
    return y;
}
// Source-over compositing of colour c with alpha ca onto (col, a); col is not premultiplied.
void put(inout float3 col, inout float a, float3 c, float ca) {
    float na = ca + a * (1. - ca);
    if (na > .001) col = (c * ca + col * a * (1. - ca)) / na;
    a = na;
}

half4 main(float2 fragCoord) {
    // 44 x 30 grid units -> 176 x 120 design units. The top 96 are the display, the rest holds the knob labels.
    float2 p = fragCoord / iResolution.xy * float2(176., 120.);
    float kind = floor(audioLow.x * 8. + .5);
    float inlv = audioLow.y;
    float outlv = audioLow.z;
    float aux = audioLow.w;
    float k1 = audioMedium.x * 100.;
    float k2 = audioMedium.y * 100.;
    float k3 = audioMedium.z * 100.;
    float3 col = float3(0.);
    float a = 0.;
    float3 blue = float3(.50, .76, 1.);
    float3 red = float3(.95, .42, .26);
    float3 bg = float3(.035, .042, .052);
    float3 gridc = float3(.14, .16, .19);

    if (p.y < 97.) {
        if (kind > .5 && kind < 1.5) {
            // Gain: pan marker, width bar, output level.
            put(col, a, bg, .55);
            float pan = (k2 - 50.) * 2.;
            float wd = k3 * .02;
            if (p.x >= 12. && p.x <= 140. && abs(p.y - 36.) < 3.) put(col, a, float3(.2, .23, .26), 1.);
            if (abs(p.x - (12. + (pan + 100.) / 200. * 128.)) < 2. && abs(p.y - 36.) < 8.) put(col, a, blue, 1.);
            if (p.x >= 12. && p.x <= 140. && abs(p.y - 62.) < 3.) put(col, a, float3(.2, .23, .26), 1.);
            if (p.x >= 12. && p.x <= 12. + wd * .5 * 128. && abs(p.y - 62.) < 3.) put(col, a, float3(.36, .66, .59), 1.);
            if (abs(p.x - 76.) < 1. && abs(p.y - 62.) < 8.) put(col, a, float3(.8, .85, .9), 1.);
            if (p.x >= 154. && p.x <= 168. && p.y >= 8. && p.y <= 90.) {
                float lv = (90. - p.y) / 82.;
                put(col, a, float3(.07, .08, .095), 1.);
                if (lv < outlv) put(col, a, mix(float3(.24, .62, .17), float3(.96, .56, .12), smoothstep(.55, .85, lv)), 1.);
            }
        }
        if (kind > 1.5 && kind < 2.5) {
            // Equaliser: response curve over the spectrum.
            float note = 15. + p.x / 176. * 120.;
            float f = 440. * pow(2., (note - 69.) / 12.);
            float w = tan(3.1415927 * f / 48000.);
            float total = shelfdb((k1 - 50.) * .3, 100., .7071, w, true) + peakdb((k2 - 50.) * .3, 1200., .9, w)
                        + shelfdb((k3 - 50.) * .3, 8000., .7071, w, false);
            total = clamp(total, -40., 16.);
            float cy = (18. - total) / 60. * 96.;
            float zy = 18. / 60. * 96.;
            put(col, a, float3(.8, .85, .9), abs(p.y - zy) < .7 ? .25 : 0.);
            if (p.y >= min(cy, zy) && p.y <= max(cy, zy)) put(col, a, float3(1., .86, .45), .16);
            float dist = abs(p.y - cy);
            put(col, a, float3(1., .86, .45), dist < 1.4 ? 1. : (dist < 2.4 ? 2.4 - dist : 0.));
        }
        if (kind > 2.5 && kind < 3.5) {
            // Compressor: transfer curve, live level dot and gain reduction bar.
            put(col, a, bg, .62);
            float thr = -48. + k1 * .48;
            float rn = k2 * .01;
            float ratio = 1. + 19. * rn * rn;
            float mk = k3 * .08;
            if (p.x >= 10. && p.x <= 148. && p.y >= 8. && p.y <= 90.) {
                float gx = (p.x - 10.) / 138.;
                float gy = (90. - p.y) / 82.;
                for (int i = 1; i < 6; i++) {
                    if (abs(gx - float(i) / 6.) < .004 || abs(gy - float(i) / 6.) < .007) put(col, a, gridc, 1.);
                }
                float xdb = -60. + gx * 60.;
                float yc = (curvec(xdb, thr, ratio, 6.) + mk + 60.) / 72.;
                if (abs(gx - (thr + 60.) / 60.) < .004) put(col, a, blue * .55, 1.);
                if (gy < yc) put(col, a, float3(.1, .2, .32), .45);
                if (abs(gy - yc) < .016) put(col, a, blue, 1.);
                float idb = inlv * 66. - 60.;
                float ix = (idb + 60.) / 60.;
                float iy = (curvec(idb, thr, ratio, 6.) + mk + 60.) / 72.;
                if (length(float2((gx - ix) * 138., (gy - iy) * 82.)) < 3.4) put(col, a, aux > .02 ? red : float3(.95, .96, .98), 1.);
            }
            if (p.x >= 154. && p.x <= 166. && p.y >= 8. && p.y <= 90.) {
                put(col, a, float3(.07, .08, .095), 1.);
                if ((p.y - 8.) / 82. < aux) put(col, a, red, 1.);
            }
        }
        if (kind > 3.5 && kind < 4.5) {
            // Saturation: transfer curve with the live operating point.
            put(col, a, bg, .62);
            float dr = k1 * .2;
            float drive = pow(10., dr / 20.);
            float ty = floor(clamp(k2, 0., 99.9) * .04);
            float m = k3 * .01;
            float ol = pow(10., -dr * .6 / 20.);
            if (p.x >= 34. && p.x <= 126. && p.y >= 8. && p.y <= 90.) {
                float gx = (p.x - 34.) / 92. * 2. - 1.;
                float gy = 1. - (p.y - 8.) / 82. * 2.;
                if (abs(gx) < .01 || abs(gy) < .012) put(col, a, gridc, 1.);
                float yc = (gx * (1. - m) + shape(gx * drive, ty) * m) * ol;
                yc = clamp(yc, -1.2, 1.2);
                if (abs(gy - yc) < .045) put(col, a, blue, 1.);
                float il = pow(10., (inlv * 66. - 60.) / 20.);
                float iy = clamp((il * (1. - m) + shape(il * drive, ty) * m) * ol, -1.2, 1.2);
                if (length(float2((gx - il) * 46., (gy - iy) * 41.)) < 3.2) put(col, a, float3(.95, .96, .98), 1.);
            }
        }
        if (kind > 4.5 && kind < 5.5) {
            // Limiter: transfer curve clipped at the ceiling, live dot and gain reduction bar.
            put(col, a, bg, .62);
            float cn = 1. - k2 * .01;
            float cdb = -12. * cn * cn;
            float c = (cdb + 30.) / 36.;
            if (p.x >= 10. && p.x <= 148. && p.y >= 8. && p.y <= 90.) {
                float gx = (p.x - 10.) / 138.;
                float gy = (90. - p.y) / 82.;
                for (int i = 1; i < 6; i++) {
                    if (abs(gx - float(i) / 6.) < .004 || abs(gy - float(i) / 6.) < .007) put(col, a, gridc, 1.);
                }
                float yc = min(gx, c);
                if (abs(gx - c) < .004) put(col, a, blue * .55, 1.);
                if (gy < yc) put(col, a, float3(.1, .2, .32), .45);
                if (abs(gy - c) < .008) put(col, a, blue * .8, 1.);
                if (abs(gy - yc) < .016) put(col, a, blue, 1.);
                float ix = clamp((inlv * 66. - 60. + k1 * .12 + 30.) / 36., 0., 1.);
                if (length(float2((gx - ix) * 138., (gy - min(ix, c)) * 82.)) < 3.4) put(col, a, aux > .02 ? red : float3(.95, .96, .98), 1.);
            }
            if (p.x >= 154. && p.x <= 166. && p.y >= 8. && p.y <= 90.) {
                put(col, a, float3(.07, .08, .095), 1.);
                if ((p.y - 8.) / 82. < aux) put(col, a, red, 1.);
            }
        }
    } else if (kind > .5) {
        float lit = 0.;
''' + label_block() + '''
        put(col, a, float3(.82, .86, .90), lit);
    }
    return half4(half3(col * a), half(a));
}
'''
Path(__file__).with_name("panel.sksl").write_text(SHADER)
