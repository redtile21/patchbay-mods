"""Writes field.nitro: an 8-band stereo analysis for the EB Visualizer's stereo field.

Per band: pan (from the left and right levels), level (-60..0 dB) and width (1 - correlation) / 2, so 0 is mono,
0.5 uncorrelated and 1 fully out of phase. Each band is one drawing lane, packed as 6-bit fields
((corr * 64 + level) * 64 + pan) * 64 + width, divided by 2^24 (exact in float32); only band 0 carries the overall
correlation.
"""
from pathlib import Path

CENTERS = [60, 150, 350, 800, 1800, 4000, 8000, 14000]
Q = 1.2
L = []
A = L.append
A("component eb_vis_field\n{\n    audio_inport in;\n\n    audio_outport out;\n    audio_outport f32<4> display;\n    audio_outport f32<4> display2;\n")
A("    f32 p_sr = 0.0;\n    f32 e_lr = 0.0;\n    f32 e_ll = 0.0;\n    f32 e_rr = 0.0;\n")
for i in range(8):
    A(f"    f32 b0_{i} = 0.0;\n    f32 b2_{i} = 0.0;\n    f32 a1_{i} = 0.0;\n    f32 a2_{i} = 0.0;\n    f32 ex{i} = 0.0;\n")
    for c in "lr":
        A(f"    f32 x1{c}{i} = 0.0;\n    f32 x2{c}{i} = 0.0;\n    f32 y1{c}{i} = 0.0;\n    f32 y2{c}{i} = 0.0;\n    f32 e{c}{i} = 0.0;\n")
A("""
    f32 bound(f32 v, f32 lo, f32 hi)
    {
        return fmax(lo, fmin(hi, v));
    }
    f32 q6(f32 v)
    {
        return floor(bound(v, 0.0, 1.0) * 63.0 + 0.5);
    }

    process
    {
        f32<> x = in;
        out = x;
        f32 sr = EC.samplerate;
        if (sr != p_sr)
        {
            // Band-pass filters (RBJ, 0 dB peak, Q 1.2) at 60, 150, 350, 800, 1.8k, 4k, 8k and 14 kHz.
            p_sr = sr;
""")
for i, f in enumerate(CENTERS):
    A(f"""            f32 w{i} = 6.283185307 * fmin({float(f)}, 0.45 * sr) / sr;
            f32 al{i} = sin(w{i}) / (2.0 * {Q});
            f32 n{i} = 1.0 + al{i};
            b0_{i} = al{i} / n{i};
            b2_{i} = 0.0 - al{i} / n{i};
            a1_{i} = -2.0 * cos(w{i}) / n{i};
            a2_{i} = (1.0 - al{i}) / n{i};
""")
A("""        }
        // Band energies over about 200 ms.
        f32 ka = 1.0 - exp(-1.0 / (0.2 * sr));
        // Overall correlation over about 300 ms.
        f32 kc = 1.0 - exp(-1.0 / (0.3 * sr));
        e_lr = e_lr + kc * (x[0] * x[1] - e_lr);
        e_ll = e_ll + kc * (x[0] * x[0] - e_ll);
        e_rr = e_rr + kc * (x[1] * x[1] - e_rr);
        f32 corr = 0.0;
        if (e_ll > 0.00000001 && e_rr > 0.00000001)
        {
            corr = bound(e_lr / sqrt(e_ll * e_rr), -1.0, 1.0);
        }
""")
for i in range(8):
    for c, idx in (("l", 0), ("r", 1)):
        A(f"""        f32 y{c}{i} = b0_{i} * x[{idx}] + b2_{i} * x2{c}{i} - a1_{i} * y1{c}{i} - a2_{i} * y2{c}{i};
        x2{c}{i} = x1{c}{i};
        x1{c}{i} = x[{idx}];
        y2{c}{i} = y1{c}{i};
        y1{c}{i} = y{c}{i};
        e{c}{i} = e{c}{i} + ka * (y{c}{i} * y{c}{i} - e{c}{i});
""")
    A(f"""        ex{i} = ex{i} + ka * (yl{i} * yr{i} - ex{i});
        f32 al_{i} = sqrt(el{i});
        f32 ar_{i} = sqrt(er{i});
        f32 pan_{i} = (ar_{i} - al_{i}) / fmax(ar_{i} + al_{i}, 0.0000001);
        f32 lv_{i} = (10.0 * log10(fmax(el{i} + er{i}, 0.000000000001)) + 60.0) / 60.0;
        f32 cb_{i} = 1.0;
        if (el{i} > 0.000000000001 && er{i} > 0.000000000001)
        {{
            cb_{i} = bound(ex{i} / sqrt(el{i} * er{i}), -1.0, 1.0);
        }}
        f32 code_{i} = ((q6(lv_{i}) * 64.0 + q6((pan_{i} + 1.0) * 0.5)) * 64.0) + q6((1.0 - cb_{i}) * 0.5);
""")
A("""        code_0 = code_0 + q6((corr + 1.0) * 0.5) * 262144.0;
        f32 s = 1.0 / 16777216.0;
        display = <code_0 * s, code_1 * s, code_2 * s, code_3 * s>;
        display2 = <code_4 * s, code_5 * s, code_6 * s, code_7 * s>;
    }
}
""")
Path(__file__).with_name("field.nitro").write_text("".join(L))
