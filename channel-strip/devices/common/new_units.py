"""Scaffold EB Gate, EB De-esser, EB Transient and EB Clipper from the compressor/limiter template."""
import shutil
import uuid
from pathlib import Path

DEV = Path.home() / "Developer/bitwig-blueprint-work/bitwig-devices-blueprint/devices"
comp_sksl = (DEV / "eb-compressor/panel.sksl").read_text()
HEAD = comp_sksl[comp_sksl.index("float sdseg"):comp_sksl.index("half4 main")]
HEAD = HEAD.replace(HEAD[HEAD.index("float curve("):HEAD.index("const float MT")], "")
UNIFORMS = "uniform float4 audioLow;\nuniform float4 audioMedium;\n\n"
SHADER_EXTRA = """float dbg(float d) { return pow(10., d / 20.); }
float todb(float v) { return 20. * log(max(v, .000001)) / log(10.); }
float3 grbarpx(float2 p, float3 color, float x0, float x1, float lvl, float pk, float3 red) {
    if (p.x >= x0 && p.x < x1 && p.y >= MT && p.y <= MB) {
        float lv = (p.y - MT) / MH;
        color = float3(.040, .042, .048);
        if (lv < lvl) color = red;
        if (abs(lv - pk) < .008 && pk > .01) color = float3(1., .80, .50);
    }
    return color;
}
"""

# ---------------------------------------------------------------- shared Nitro pieces

NITRO_FUNCS = """
    f32 dbgain(f32 v)
    {
        return exp(v * 0.11512925464970229);
    }
    f32 bound(f32 v, f32 lo, f32 hi)
    {
        return fmax(lo, fmin(hi, v));
    }
    f32 todb(f32 v)
    {
        return 20.0 * log10(fmax(0.000001, v));
    }
"""

METER_STATE = """
    i32 runtime_magic = 0;
    f32 in_env = 0.0;
    f32 out_env = 0.0;
    f32 in_pk = 0.0;
    f32 out_pk = 0.0;
    f32 t_in = 0.0;
    f32 t_out = 0.0;
    f32 gr_pk = 0.0;
    f32 t_gr = 0.0;
    f32 t_disp = 0.0;
    f32 disp_gr = 0.0;
"""

METER_INIT = """            in_env = 0.0;
            out_env = 0.0;
            in_pk = 0.0;
            out_pk = 0.0;
            t_in = 0.0;
            t_out = 0.0;
            gr_pk = 0.0;
            t_gr = 0.0;
            t_disp = 0.0;
            disp_gr = 0.0;
"""


def meter_block(gr_scale):
    """Needs pin, pout (linear peaks) and gr_now (dB >= 0); defines gr_code (bar now, number held)."""
    return f"""
        // Meters: decaying envelopes, five-second peak holds, gain change held for the number.
        in_env = fmax(pin, in_env * 0.9998);
        out_env = fmax(pout, out_env * 0.9998);
        f32 hold_len = 5.0 * sr;
        if (pin >= in_pk)
        {{
            in_pk = pin;
            t_in = 0.0;
        }}
        else
        {{
            t_in = t_in + 1.0;
            if (t_in > hold_len)
            {{
                in_pk = pin;
                t_in = 0.0;
            }}
        }}
        if (pout >= out_pk)
        {{
            out_pk = pout;
            t_out = 0.0;
        }}
        else
        {{
            t_out = t_out + 1.0;
            if (t_out > hold_len)
            {{
                out_pk = pout;
                t_out = 0.0;
            }}
        }}
        if (gr_now >= gr_pk)
        {{
            gr_pk = gr_now;
            t_gr = 0.0;
        }}
        else
        {{
            t_gr = t_gr + 1.0;
            if (t_gr > hold_len)
            {{
                gr_pk = gr_now;
                t_gr = 0.0;
            }}
        }}
        t_disp = t_disp + 1.0;
        if (t_disp > 1.0 * sr)
        {{
            disp_gr = gr_pk;
            t_disp = 0.0;
        }}
        f32 gr_i = floor(bound(gr_now / {gr_scale:.1f}, 0.0, 1.0) * 240.0 + 0.5);
        f32 gh_i = floor(bound(disp_gr / {gr_scale:.1f}, 0.0, 1.0) * 240.0 + 0.5);
        f32 gr_code = (gr_i * 256.0 + gh_i) / 65536.0;
"""


def gr_decode(scale):
    return f"""    float gcode = audioMedium.x * 65536.;
    float gri = floor(gcode / 256. + .0001);
    float ghi = gcode - gri * 256.;
    float grbar = gri / 240.;
    float grpk = ghi / 240.;
    float gr = ghi / 240. * {scale:.1f};
    float grlive = gri / 240. * {scale:.1f};
"""


SHADER_COLORS = """    float3 color = float3(.060, .064, .072);
    float3 grid = float3(.150, .160, .175);
    float3 blue = float3(.30, .68, .92);
    float3 red = float3(.98, .52, .14);
    float3 txt = float3(.80, .82, .84);
"""

UNITS = {}

# ---------------------------------------------------------------- EB Gate

UNITS["gate"] = dict(
    name="EB Gate", nitro_name="gate.nitro",
    description="Elodea Blackstar noise gate and downward expander with hold, hysteresis and sidechain filter.",
    spec='''# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB gate expander noise dynamics",
    "decimals": [
        ("Threshold", "THRESHOLD", -80.0, 0.0, -50.0, 1, "Threshold in dB", "threshold"),
        ("Range", "RANGE", 0.0, 80.0, 40.0, 0, "How far the gate closes, in dB", "range_db"),
        ("Hysteresis", "HYSTERESIS", 0.0, 12.0, 3.0, 1, "The gate closes this many dB below the threshold", "hysteresis"),
        ("Attack", "ATTACK", 0.05, 50.0, 0.5, 2, "Opening time in ms", "attack"),
        ("Hold", "HOLD", 0.0, 500.0, 50.0, 0, "Time kept open after the signal falls, in ms", "hold"),
        ("Release", "RELEASE", 5.0, 2000.0, 150.0, 0, "Closing time in ms", "release"),
        ("Sidechain HPF", "SC_HPF", 0.0, 500.0, 0.0, 0, "Detector high-pass in Hz, below 20 is off", "sc_hpf"),
    ],
    "cols": 3, "display_w": 80,
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1)],
    "titles": {"SC_HPF": "SC HPF", "HYSTERESIS": "Hyst"},
    "chooser_col": [(1, 29)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 1,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [
        ("Mode", "MODE", ("Gate", "Expander"), 0, "Gate: closes by the range below the threshold. Expander: 1:2 below the threshold, at most the range", "mode"),
    ],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
''',
    nitro=f"""component eb_gate
{{
    audio_inport in;
    audio_inport f32 threshold = -50.0;
    audio_inport f32 range_db = 40.0;
    audio_inport f32 hysteresis = 3.0;
    audio_inport f32 attack = 0.5;
    audio_inport f32 hold = 50.0;
    audio_inport f32 release = 150.0;
    audio_inport f32 sc_hpf = 0.0;
    value_inport i32 mode;

    audio_outport out;
    audio_outport f32<4> display;
    audio_outport f32<4> display2;
{METER_STATE}
    f32 env = 0.0;
    f32 g_db = 0.0;
    i32 is_open = 0;
    f32 hold_n = 0.0;
    f32 hp1 = 0.0;
    f32 hp1x = 0.0;
    f32 hp2 = 0.0;
    f32 hp2x = 0.0;
{NITRO_FUNCS}
    reset
    {{
        runtime_magic = 0;
    }}

    process
    {{
        if (runtime_magic != 715311)
        {{
            runtime_magic = 715311;
{METER_INIT}            env = 0.0;
            g_db = 0.0;
            is_open = 0;
            hold_n = 0.0;
            hp1 = 0.0;
            hp1x = 0.0;
            hp2 = 0.0;
            hp2x = 0.0;
        }}
        f32 sr = EC.samplerate;
        f32<> x = in;

        // Detector: linked peak, or the mono sum through two one-pole high-passes.
        f32 det = fmax(fabs(x[0]), fabs(x[1]));
        if (sc_hpf >= 20.0)
        {{
            f32 m = 0.5 * (x[0] + x[1]);
            f32 a = exp(-6.283185307 * bound(sc_hpf, 20.0, 500.0) / sr);
            hp1 = a * (hp1 + m - hp1x);
            hp1x = m;
            hp2 = a * (hp2 + hp1 - hp2x);
            hp2x = hp1;
            det = fabs(hp2);
        }}
        env = fmax(det, env * exp(-1.0 / (0.005 * sr)));
        f32 lvl = todb(env);
        f32 thr = bound(threshold, -80.0, 0.0);
        f32 rng = bound(range_db, 0.0, 80.0);

        f32 target = 0.0;
        if (mode == 1)
        {{
            // Expander 1:2 below the threshold, at most the range.
            target = bound(lvl - thr, 0.0 - rng, 0.0);
        }}
        else
        {{
            // Gate: opens above the threshold, closes below threshold minus hysteresis once the hold has run out.
            if (lvl > thr)
            {{
                is_open = 1;
                hold_n = bound(hold, 0.0, 500.0) * 0.001 * sr;
            }}
            else
            {{
                if (hold_n > 0.0)
                {{
                    hold_n = hold_n - 1.0;
                }}
                else
                {{
                    if (lvl < thr - bound(hysteresis, 0.0, 12.0))
                    {{
                        is_open = 0;
                    }}
                }}
            }}
            if (is_open == 0)
            {{
                target = 0.0 - rng;
            }}
        }}
        f32 att = exp(-1.0 / (bound(attack, 0.05, 50.0) * 0.001 * sr));
        f32 rel = exp(-1.0 / (bound(release, 5.0, 2000.0) * 0.001 * sr));
        if (target > g_db)
        {{
            g_db = att * g_db + (1.0 - att) * target;
        }}
        else
        {{
            g_db = rel * g_db + (1.0 - rel) * target;
        }}
        f32<> y = x * dbgain(g_db);
        out = y;

        f32 pin = fmax(fabs(x[0]), fabs(x[1]));
        f32 pout = fmax(fabs(y[0]), fabs(y[1]));
        f32 gr_now = 0.0 - g_db;
{meter_block(80.0)}
        f32 ine = bound((todb(in_env) + 80.0) / 80.0, 0.0, 1.0);
        f32 oute = bound((todb(out_env) + 80.0) / 80.0, 0.0, 1.0);
        f32 inp = bound((todb(in_pk) + 80.0) / 80.0, 0.0, 1.0);
        f32 outp = bound((todb(out_pk) + 80.0) / 80.0, 0.0, 1.0);
        display = <(thr + 80.0) / 80.0, rng / 80.0, cast(mode, f32), ine>;
        display2 = <gr_code, oute, inp, outp>;
    }}
}}
""",
    shader=f"""// audioLow:    threshold (0..1 = -80..0 dB), range (0..1 = 0..80 dB), mode (0 gate, 1 expander), input level (-80..0 dB)
// audioMedium: gain reduction (bar now / number held, 0..80 dB), output level, input peak hold, output peak hold (-80..0 dB)
{UNIFORMS}{HEAD}{SHADER_EXTRA}
float gcurve(float x, float t, float r, float m) {{
    if (x >= t) return x;
    if (m > .5) return max(t + (x - t) * 2., x - r);
    return x - r;
}}

half4 main(float2 fragCoord) {{
    // 80 x 47 grid units -> 320 x 188 design units.
    float2 p = fragCoord / iResolution.xy * float2(320., 188.);
{SHADER_COLORS}
    float thr = -80. + audioLow.x * 80.;
    float rng = audioLow.y * 80.;
    float md = audioLow.z;
    float inlv = audioLow.w;
{gr_decode(80.0)}
    color = meterpx(p, color, 6., 30., inlv, audioMedium.z, audioLow.x);
    color = meterpx(p, color, 290., 314., audioMedium.y, audioMedium.w, -1.);
    color = grbarpx(p, color, 266., 278., grbar, grpk, red);

    // Transfer curve: input -80..0 dB against output -80..0 dB.
    if (p.x >= 36. && p.x <= 260. && p.y >= MT && p.y <= MB) {{
        color = float3(.038, .046, .056);
        float gx = (p.x - 36.) / 224.;
        float gy = (MB - p.y) / MH;
        for (int i = 1; i < 8; i++) {{
            if (abs(gx - float(i) / 8.) < .002) color = grid;
            if (abs(gy - float(i) / 8.) < .004) color = grid;
        }}
        float yc = (gcurve(-80. + gx * 80., thr, rng, md) + 80.) / 80.;
        if (abs(gx - audioLow.x) < .0022) color = blue * .55;
        if (gy < yc) color = color * .65 + float3(.05, .10, .16) * .55;
        if (abs(gy - yc) < .01) color = float3(.50, .76, 1.);
        float iny = (gcurve(-80. + inlv * 80., thr, rng, md) + 80.) / 80.;
        float2 d = float2((gx - inlv) * 224., (gy - iny) * MH);
        if (length(d) < 3.2) color = grlive > 1. ? red : float3(.95, .96, .98);
    }}

    float inpk = audioMedium.z * 80. - 80.;
    float outpk = audioMedium.w * 80. - 80.;
    if (number(p, float2(8., 7.), 8., inpk) > .5) color = numcol(inpk, -.1);
    if (number(p, float2(292., 7.), 8., outpk) > .5) color = numcol(outpk, -.1);
    if (number(p, float2(250., 7.), 8., -gr) > .5) color = gr > .05 ? red : txt;
    if (number(p, float2(62., 7.), 8., thr) > .5) color = blue;
    return half4(half3(color), 1.);
}}
""",
    knobs=("THRESHOLD", "RANGE", "RELEASE"),
    params=("THRESHOLD", "RANGE", "HYSTERESIS", "ATTACK", "HOLD", "RELEASE", "SC_HPF", "MODE"),
)

# ---------------------------------------------------------------- EB De-esser

UNITS["deesser"] = dict(
    name="EB De-esser", nitro_name="deesser.nitro",
    description="Elodea Blackstar de-esser: turns down sibilance above a frequency, as a split band or the whole signal.",
    spec='''# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB de-esser deesser sibilance vocal dynamics",
    "decimals": [
        ("Frequency", "FREQ", 2000.0, 12000.0, 6000.0, 0, "Sibilance detector and split frequency in Hz", "freq"),
        ("Threshold", "THRESHOLD", -60.0, 0.0, -30.0, 1, "Threshold in dB", "threshold"),
        ("Range", "RANGE", 0.0, 24.0, 8.0, 1, "Most reduction in dB", "range_db"),
        ("Release", "RELEASE", 10.0, 500.0, 60.0, 0, "Release time in ms", "release"),
    ],
    "cols": 2, "display_w": 56,
    "titles": {"FREQ": "Freq"},
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 1,
    "meters": {}, "vectors": 2, "display_h": 47,
    "chooser_col": [(1, 30)],
    "free_labels": [(1, 25, 15, "MODE")],
    "choices": [
        ("Mode", "MODE", ("Split", "Wide"), 0, "Split: turn down only above the frequency. Wide: turn down the whole signal", "mode"),
    ],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
''',
    nitro=f"""component eb_deesser
{{
    audio_inport in;
    audio_inport f32 freq = 6000.0;
    audio_inport f32 threshold = -30.0;
    audio_inport f32 range_db = 8.0;
    audio_inport f32 release = 60.0;
    value_inport i32 mode;

    audio_outport out;
    audio_outport f32<4> display;
    audio_outport f32<4> display2;
{METER_STATE}
    f32 p_f = 0.0;
    f32 p_sr = 0.0;
    f32 b0 = 1.0;
    f32 b1 = 0.0;
    f32 b2 = 0.0;
    f32 a1 = 0.0;
    f32 a2 = 0.0;
    f32 k_lp = 0.0;
    f32 z1 = 0.0;
    f32 z2 = 0.0;
    f32<2> lp = 0.0;
    f32 env = 0.0;
    f32 sib_env = 0.0;
{NITRO_FUNCS}
    reset
    {{
        runtime_magic = 0;
    }}

    process
    {{
        if (runtime_magic != 715322)
        {{
            runtime_magic = 715322;
{METER_INIT}            z1 = 0.0;
            z2 = 0.0;
            lp = 0.0;
            env = 0.0;
            sib_env = 0.0;
            p_f = 0.0;
        }}
        f32 sr = EC.samplerate;
        f32 f = bound(freq, 2000.0, fmin(12000.0, 0.45 * sr));
        if (f != p_f || sr != p_sr)
        {{
            p_f = f;
            p_sr = sr;
            // Detector: second-order high-pass (RBJ, Q 0.707) at the frequency.
            f32 w = 6.283185307 * f / sr;
            f32 cw = cos(w);
            f32 al = sin(w) / (2.0 * 0.7071);
            f32 a0 = 1.0 + al;
            b0 = (1.0 + cw) * 0.5 / a0;
            b1 = 0.0 - (1.0 + cw) / a0;
            b2 = (1.0 + cw) * 0.5 / a0;
            a1 = -2.0 * cw / a0;
            a2 = (1.0 - al) / a0;
            // Split: complementary one-pole low-pass, so low + high rebuilds the input exactly.
            k_lp = 1.0 - exp(-6.283185307 * f / sr);
        }}
        f32<> x = in;
        f32 m = 0.5 * (x[0] + x[1]);
        f32 h = b0 * m + z1;
        z1 = b1 * m - a1 * h + z2;
        z2 = b2 * m - a2 * h;
        f32 det = fabs(h);
        f32 att = exp(-1.0 / (0.0005 * sr));
        f32 rel = exp(-1.0 / (bound(release, 10.0, 500.0) * 0.001 * sr));
        if (det > env)
        {{
            env = att * env + (1.0 - att) * det;
        }}
        else
        {{
            env = rel * env + (1.0 - rel) * det;
        }}
        f32 thr = bound(threshold, -60.0, 0.0);
        f32 rng = bound(range_db, 0.0, 24.0);
        // Ratio 4:1 above the threshold, at most the range.
        f32 gr_now = bound((todb(env) - thr) * 0.75, 0.0, rng);
        f32 g = dbgain(0.0 - gr_now);
        lp = lp + k_lp * (x - lp);
        f32<> y = x * g;
        if (mode == 0)
        {{
            y = lp + (x - lp) * g;
        }}
        out = y;

        sib_env = fmax(det, sib_env * 0.9995);
        f32 pin = fmax(fabs(x[0]), fabs(x[1]));
        f32 pout = fmax(fabs(y[0]), fabs(y[1]));
{meter_block(24.0)}
        f32 sib = bound((todb(sib_env) + 60.0) / 60.0, 0.0, 1.0);
        f32 oute = bound((todb(out_env) + 60.0) / 60.0, 0.0, 1.0);
        f32 outp = bound((todb(out_pk) + 60.0) / 60.0, 0.0, 1.0);
        display = <(f - 2000.0) / 10000.0, (thr + 60.0) / 60.0, rng / 24.0, sib>;
        display2 = <gr_code, oute, cast(mode, f32), outp>;
    }}
}}
""",
    shader=f"""// audioLow:    frequency (0..1 = 2..12 kHz), threshold (0..1 = -60..0 dB), range (0..1 = 0..24 dB), sibilance level (-60..0 dB)
// audioMedium: gain reduction (bar now / number held, 0..24 dB), output level, mode (0 split, 1 wide), output peak hold
{UNIFORMS}{HEAD}{SHADER_EXTRA}
// Response of low + g * high for the one-pole split at f, in dB.
float splitdb(float fx, float f, float g, float wide) {{
    if (wide > .5) return todb(g);
    float s = fx / f;
    return 10. * log((1. + g * g * s * s) / (1. + s * s)) / log(10.);
}}

half4 main(float2 fragCoord) {{
    // 56 x 47 grid units -> 224 x 188 design units.
    float2 p = fragCoord / iResolution.xy * float2(224., 188.);
{SHADER_COLORS}
    float f = 2000. + audioLow.x * 10000.;
    float rng = audioLow.z * 24.;
    float wide = audioMedium.z;
{gr_decode(24.0)}
    color = meterpx(p, color, 6., 30., audioLow.w, -1., audioLow.y);
    color = meterpx(p, color, 194., 218., audioMedium.y, audioMedium.w, -1.);
    color = grbarpx(p, color, 172., 184., grbar, grpk, red);

    // Response: 500 Hz .. 20 kHz across, -24 .. +6 dB up; the range dimmed, the live reduction bright.
    if (p.x >= 36. && p.x <= 166. && p.y >= MT && p.y <= MB) {{
        color = float3(.038, .046, .056);
        float gx = (p.x - 36.) / 130.;
        float gy = (MB - p.y) / MH;
        float fx = 500. * pow(40., gx);
        for (int i = 1; i < 5; i++) {{
            if (abs(gy - float(i) / 5.) < .004) color = grid;
        }}
        float fl = log(f / 500.) / log(40.);
        if (abs(gx - fl) < .004) color = blue * .55;
        float y0 = 24. / 30.;
        if (abs(gy - y0) < .004) color = grid * 1.6;
        float yr = (splitdb(fx, f, dbg(-rng), wide) + 24.) / 30.;
        if (abs(gy - yr) < .006) color = blue * .45;
        float yl = (splitdb(fx, f, dbg(-grlive), wide) + 24.) / 30.;
        if (gy < yl) color = color * .65 + float3(.05, .10, .16) * .55;
        if (abs(gy - yl) < .011) color = grlive > .3 ? red : float3(.50, .76, 1.);
    }}

    float opk = audioMedium.w * 60. - 60.;
    if (number(p, float2(196., 7.), 8., opk) > .5) color = numcol(opk, -.1);
    if (number(p, float2(158., 7.), 8., -gr) > .5) color = gr > .05 ? red : txt;
    if (number(p, float2(62., 7.), 8., f / 1000.) > .5) color = blue;
    return half4(half3(color), 1.);
}}
""",
    knobs=("FREQ", "THRESHOLD", "RANGE"),
    params=("FREQ", "THRESHOLD", "RANGE", "RELEASE", "MODE"),
)

# ---------------------------------------------------------------- EB Transient

UNITS["transient"] = dict(
    name="EB Transient", nitro_name="transient.nitro",
    description="Elodea Blackstar transient shaper: more or less attack and sustain, independent of level.",
    spec='''# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB transient shaper attack sustain punch drums dynamics",
    "decimals": [
        ("Attack", "ATTACK", -100.0, 100.0, 0.0, 0, "More (positive) or less (negative) attack, in percent", "attack"),
        ("Sustain", "SUSTAIN", -100.0, 100.0, 0.0, 0, "More (positive) or less (negative) sustain, in percent", "sustain"),
        ("Output", "OUTPUT", -24.0, 6.0, 0.0, 1, "Output level in dB", "output"),
        ("Mix", "MIX", 0.0, 100.0, 100.0, 0, "Dry/wet mix in percent", "mix"),
    ],
    "cols": 2, "display_w": 56,
    "knob_pos": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 1,
    "meters": {}, "vectors": 2, "display_h": 47,
    "chooser_col": [(1, 30)],
    "free_labels": [(1, 25, 15, "SPEED")],
    "choices": [
        ("Speed", "SPEED", ("Fast", "Medium", "Slow"), 1, "How long a transient lasts: Fast for clicks and hats, Slow for toms and bass", "speed"),
    ],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
''',
    nitro=f"""component eb_transient
{{
    audio_inport in;
    audio_inport f32 attack = 0.0;
    audio_inport f32 sustain = 0.0;
    audio_inport f32 output = 0.0;
    audio_inport f32 mix = 100.0;
    value_inport i32 speed;

    audio_outport out;
    audio_outport f32<4> display;
    audio_outport f32<4> display2;
{METER_STATE}
    f32 fast = 0.0;
    f32 slow = 0.0;
    f32 g_s = 0.0;
{NITRO_FUNCS}
    reset
    {{
        runtime_magic = 0;
    }}

    process
    {{
        if (runtime_magic != 715333)
        {{
            runtime_magic = 715333;
{METER_INIT}            fast = 0.0;
            slow = 0.0;
            g_s = 0.0;
        }}
        f32 sr = EC.samplerate;
        f32<> x = in;
        f32 pk = fmax(fabs(x[0]), fabs(x[1]));

        // Two envelopes: fast follows the hit, slow lags it; their difference marks attack (+) and sustain (-).
        f32 s_att = 25.0;
        f32 s_rel = 200.0;
        if (speed == 0)
        {{
            s_att = 10.0;
            s_rel = 100.0;
        }}
        if (speed == 2)
        {{
            s_att = 50.0;
            s_rel = 400.0;
        }}
        f32 fa = exp(-1.0 / (0.0003 * sr));
        f32 fr = exp(-1.0 / (0.020 * sr));
        f32 sa = exp(-1.0 / (s_att * 0.001 * sr));
        f32 sr2 = exp(-1.0 / (s_rel * 0.001 * sr));
        if (pk > fast)
        {{
            fast = fa * fast + (1.0 - fa) * pk;
        }}
        else
        {{
            fast = fr * fast + (1.0 - fr) * pk;
        }}
        if (pk > slow)
        {{
            slow = sa * slow + (1.0 - sa) * pk;
        }}
        else
        {{
            slow = sr2 * slow + (1.0 - sr2) * pk;
        }}
        f32 diff = todb(fast) - todb(slow);
        f32 av = bound(attack, -100.0, 100.0) * 0.01;
        f32 sv = bound(sustain, -100.0, 100.0) * 0.01;
        f32 gdb = av * fmax(diff, 0.0) * 1.5 + sv * fmax(0.0 - diff, 0.0) * 1.5;
        gdb = bound(gdb, -18.0, 18.0);
        if (slow < 0.0001)
        {{
            gdb = 0.0;
        }}
        f32 gk = 1.0 - exp(-1.0 / (0.001 * sr));
        g_s = g_s + gk * (gdb - g_s);
        f32 mx = bound(mix, 0.0, 100.0) * 0.01;
        f32 g = (mx * dbgain(g_s) + (1.0 - mx)) * dbgain(bound(output, -24.0, 6.0));
        f32<> y = x * g;
        out = y;

        f32 pin = pk;
        f32 pout = fmax(fabs(y[0]), fabs(y[1]));
        f32 gr_now = fmax(0.0, 0.0 - g_s);
{meter_block(18.0)}
        f32 ine = bound((todb(in_env) + 60.0) / 60.0, 0.0, 1.0);
        f32 oute = bound((todb(out_env) + 60.0) / 60.0, 0.0, 1.0);
        f32 inp = bound((todb(in_pk) + 60.0) / 60.0, 0.0, 1.0);
        f32 outp = bound((todb(out_pk) + 60.0) / 60.0, 0.0, 1.0);
        display = <(av + 1.0) * 0.5, (sv + 1.0) * 0.5, (g_s + 18.0) / 36.0, ine>;
        display2 = <inp, oute, outp, 0.0>;
    }}
}}
""",
    shader=f"""// audioLow:    attack (0..1 = -100..100 %), sustain (0..1 = -100..100 %), live gain change (0..1 = -18..+18 dB), input level (-60..0 dB)
// audioMedium: input peak hold, output level, output peak hold (-60..0 dB), reserved
{UNIFORMS}{HEAD}{SHADER_EXTRA}
// A drum hit's envelope over 0..1 of the window: a short rise, then an exponential tail.
float hit(float t) {{
    return t < .05 ? t / .05 : exp(-(t - .05) * 3.6);
}}

half4 main(float2 fragCoord) {{
    // 56 x 47 grid units -> 224 x 188 design units.
    float2 p = fragCoord / iResolution.xy * float2(224., 188.);
{SHADER_COLORS}
    float av = audioLow.x * 2. - 1.;
    float sv = audioLow.y * 2. - 1.;
    float gnow = audioLow.z * 36. - 18.;

    color = meterpx(p, color, 6., 30., audioLow.w, audioMedium.x, -1.);
    color = meterpx(p, color, 194., 218., audioMedium.y, audioMedium.z, -1.);

    // Live gain change, from the centre: up (blue) for more, down (amber) for less.
    if (p.x >= 172. && p.x < 184. && p.y >= MT && p.y <= MB) {{
        float lv = (MB - p.y) / MH * 2. - 1.;
        float gn = gnow / 18.;
        color = float3(.040, .042, .048);
        if (lv >= 0. && lv < gn) color = blue;
        if (lv < 0. && lv > gn) color = red;
        if (abs(lv) < .012) color = grid * 1.6;
    }}

    // A hit before (grey) and after (blue) shaping.
    if (p.x >= 36. && p.x <= 166. && p.y >= MT && p.y <= MB) {{
        color = float3(.038, .046, .056);
        float t = (p.x - 36.) / 130.;
        float gy = (MB - p.y) / MH;
        for (int i = 1; i < 5; i++) {{
            if (abs(gy - float(i) / 5.) < .004) color = grid;
        }}
        float e = hit(t);
        float wa = 1. - smoothstep(.04, .20, t);
        float ws = smoothstep(.10, .45, t);
        float gdb = av * 9. * wa + sv * 9. * ws;
        float es = e * dbg(gdb);
        float y0 = e / 1.9;
        float y1 = min(es / 1.9, .99);
        if (gy < y0) color = color * .6 + float3(.10, .11, .12) * .7;
        if (gy < y1) color = color * .65 + float3(.05, .10, .16) * .55;
        if (abs(gy - y0) < .006) color = float3(.36, .38, .41);
        if (abs(gy - y1) < .011) color = float3(.50, .76, 1.);
    }}

    float ipk = audioMedium.x * 60. - 60.;
    float opk = audioMedium.z * 60. - 60.;
    if (number(p, float2(8., 7.), 8., ipk) > .5) color = numcol(ipk, -.1);
    if (number(p, float2(196., 7.), 8., opk) > .5) color = numcol(opk, -.1);
    if (number(p, float2(158., 7.), 8., gnow) > .5) color = gnow < -.05 ? red : (gnow > .05 ? blue : txt);
    return half4(half3(color), 1.);
}}
""",
    knobs=("ATTACK", "SUSTAIN", "OUTPUT"),
    params=("ATTACK", "SUSTAIN", "OUTPUT", "MIX", "SPEED"),
)

# ---------------------------------------------------------------- EB Clipper

UNITS["clipper"] = dict(
    name="EB Clipper", nitro_name="clipper.nitro",
    description="Elodea Blackstar clipper: catches peaks at a ceiling, from hard to soft.",
    spec='''# name, identifier, min, max, default, digits, tooltip, nitro port name
SPEC = {
    "keywords": "elodea blackstar EB clipper clip soft clip peaks loudness",
    "decimals": [
        ("Input Gain", "INPUT_GAIN", 0.0, 24.0, 0.0, 1, "Input gain in dB", "input_gain"),
        ("Ceiling", "CEILING", -12.0, 0.0, -1.0, 1, "Output ceiling in dBFS", "ceiling"),
        ("Softness", "SOFTNESS", 0.0, 100.0, 30.0, 0, "0 is a hard clip; higher starts rounding the peaks earlier", "softness"),
    ],
    "cols": 2, "display_w": 56,
    "titles": {"INPUT_GAIN": "Input"},
    "knob_pos": [(0, 0), (0, 1), (1, 0)],
    "knob_size": 1, "knob_w": 15, "knob_h": 12, "pitch_x": 16, "pitch_y": 12, "row0": 0, "chooser_style": 0, "revision": 1,
    "meters": {}, "vectors": 2, "display_h": 47,
    "choices": [],
    "preflight_extra": {"recallSafety": {"canary": "runtime_magic", "arrays": []}},
}
''',
    nitro=f"""component eb_clipper
{{
    audio_inport in;
    audio_inport f32 input_gain = 0.0;
    audio_inport f32 ceiling = -1.0;
    audio_inport f32 softness = 30.0;

    audio_outport out;
    audio_outport f32<4> display;
    audio_outport f32<4> display2;
{METER_STATE}{NITRO_FUNCS}
    // Linear below the knee, then a curve that meets the ceiling smoothly (slope 1 where it starts).
    f32 clipv(f32 v, f32 c, f32 t)
    {{
        f32 a = fabs(v);
        f32 r = a;
        if (a > t)
        {{
            f32 u = (a - t) / fmax(c - t, 0.000001);
            r = fmin(c, t + (c - t) * u / (1.0 + u));
        }}
        if (v < 0.0)
        {{
            r = 0.0 - r;
        }}
        return r;
    }}

    reset
    {{
        runtime_magic = 0;
    }}

    process
    {{
        if (runtime_magic != 715344)
        {{
            runtime_magic = 715344;
{METER_INIT}        }}
        f32 sr = EC.samplerate;
        f32 ing = bound(input_gain, 0.0, 24.0);
        f32 cdb = bound(ceiling, -12.0, 0.0);
        f32 c = dbgain(cdb);
        f32 k = bound(softness, 0.0, 100.0) * 0.01;
        f32 t = c * (1.0 - 0.75 * k);
        f32<> v = in * dbgain(ing);
        f32<> y = <clipv(v[0], c, t), clipv(v[1], c, t)>;
        out = y;

        f32 pin = fmax(fabs(v[0]), fabs(v[1]));
        f32 pout = fmax(fabs(y[0]), fabs(y[1]));
        f32 gr_now = fmax(0.0, todb(pin) - todb(pout));
{meter_block(12.0)}
        f32 ine = bound((todb(in_env) + 30.0) / 36.0, 0.0, 1.0);
        f32 oute = bound((todb(out_env) + 30.0) / 36.0, 0.0, 1.0);
        f32 inp = bound((todb(in_pk) + 30.0) / 36.0, 0.0, 1.0);
        f32 outp = bound((todb(out_pk) + 30.0) / 36.0, 0.0, 1.0);
        display = <ing / 24.0, (cdb + 12.0) / 12.0, k, ine>;
        display2 = <gr_code, oute, inp, outp>;
    }}
}}
""",
    shader=f"""// audioLow:    input gain (0..1 = 0..24 dB), ceiling (0..1 = -12..0 dB), softness (0..1), input level after gain (-30..+6 dB)
// audioMedium: clip amount (bar now / number held, 0..12 dB), output level, input peak hold, output peak hold (-30..+6 dB)
{UNIFORMS}{HEAD}{SHADER_EXTRA}
float clipv(float a, float c, float t) {{
    if (a <= t) return a;
    float u = (a - t) / max(c - t, .000001);
    return min(c, t + (c - t) * u / (1. + u));
}}

half4 main(float2 fragCoord) {{
    // 56 x 47 grid units -> 224 x 188 design units.
    float2 p = fragCoord / iResolution.xy * float2(224., 188.);
{SHADER_COLORS}
    float cdb = audioLow.y * 12. - 12.;
    float c = dbg(cdb);
    float k = audioLow.z;
    float t = c * (1. - .75 * k);
    float cn = (cdb + 30.) / 36.;
{gr_decode(12.0)}
    color = meterpx(p, color, 6., 30., audioLow.w, audioMedium.z, -1.);
    color = meterpx(p, color, 194., 218., audioMedium.y, audioMedium.w, cn);
    color = grbarpx(p, color, 172., 184., grbar, grpk, red);

    // Transfer curve: input -30..+6 dB against output, rounding into the ceiling.
    if (p.x >= 36. && p.x <= 166. && p.y >= MT && p.y <= MB) {{
        color = float3(.038, .046, .056);
        float gx = (p.x - 36.) / 130.;
        float gy = (MB - p.y) / MH;
        for (int i = 1; i < 6; i++) {{
            if (abs(gx - float(i) / 6.) < .0025) color = grid;
            if (abs(gy - float(i) / 6.) < .004) color = grid;
        }}
        float yc = (todb(clipv(dbg(-30. + gx * 36.), c, t)) + 30.) / 36.;
        if (gy < yc) color = color * .65 + float3(.05, .10, .16) * .55;
        if (abs(gy - cn) < .005) color = blue * .8;
        if (abs(gy - yc) < .011) color = float3(.50, .76, 1.);
        float iny = (todb(clipv(dbg(-30. + audioLow.w * 36.), c, t)) + 30.) / 36.;
        float2 d = float2((gx - audioLow.w) * 130., (gy - iny) * MH);
        if (length(d) < 3.2) color = grlive > .3 ? red : float3(.95, .96, .98);
    }}

    float ipk = audioMedium.z * 36. - 30.;
    float opk = audioMedium.w * 36. - 30.;
    if (number(p, float2(8., 7.), 8., ipk) > .5) color = numcol(ipk, .05);
    if (number(p, float2(196., 7.), 8., opk) > .5) color = numcol(opk, .05);
    if (number(p, float2(158., 7.), 8., -gr) > .5) color = gr > .05 ? red : txt;
    if (number(p, float2(62., 7.), 8., cdb) > .5) color = blue;
    return half4(half3(color), 1.);
}}
""",
    knobs=("INPUT_GAIN", "CEILING", "SOFTNESS"),
    params=("INPUT_GAIN", "CEILING", "SOFTNESS"),
)


def main():
    tmpl = DEV / "eb-limiter"
    for key, u in UNITS.items():
        d = DEV / f"eb-{key}"
        d.mkdir(exist_ok=True)
        for f in ("build.py", "make_project.py"):
            shutil.copy(tmpl / f, d / f)
        meta = d / "meta.py"
        uid = None
        if meta.exists():
            for line in meta.read_text().splitlines():
                if line.startswith("UUID"):
                    uid = line.split('"')[1]
        uid = uid or str(uuid.uuid4())
        meta.write_text(f'NAME = "{u["name"]}"\nPROJECT_ID = "elodea-blackstar.{key}"\nUUID = "{uid}"\n'
                        f'DESCRIPTION = "{u["description"]}"\nNITRO = "{u["nitro_name"]}"\n')
        (d / "spec.py").write_text(u["spec"])
        (d / u["nitro_name"]).write_text(u["nitro"])
        (d / "panel.sksl").write_text(u["shader"])
        print(key, uid)


if __name__ == "__main__":
    main()
