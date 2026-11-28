"""Generate slot.nitro: one strip slot that can be Bypass, Gain, EQ, Compressor, Saturation or Limiter.
Three macro knobs (0..100, default 50) are mapped to the three most important parameters of the chosen unit."""
from pathlib import Path

NITRO = r'''component eb_slot
{
    audio_inport in;
    audio_inport f32 k1 = 50.0;
    audio_inport f32 k2 = 50.0;
    audio_inport f32 k3 = 50.0;
    value_inport i32 kind;

    audio_outport out;
    audio_outport f32<4> display;
    audio_outport f32<4> display2;

    f32<2>[1024] dl;
    f32[1024] gt_buf;
    i32 runtime_magic = 0;
    i32 wp = 0;
    i32 p_kind = -1;
    f32 p_k1 = -999.0;
    f32 p_k2 = -999.0;
    f32 p_k3 = -999.0;
    f32 in_env = 0.0;
    f32 out_env = 0.0;
    f32 gr_db = 0.0;
    f32 lgain = 1.0;
    f32 b0_a = 1.0;
    f32 b1_a = 0.0;
    f32 b2_a = 0.0;
    f32 a1_a = 0.0;
    f32 a2_a = 0.0;
    f32<2> z1_a = 0.0;
    f32<2> z2_a = 0.0;
    f32 b0_b = 1.0;
    f32 b1_b = 0.0;
    f32 b2_b = 0.0;
    f32 a1_b = 0.0;
    f32 a2_b = 0.0;
    f32<2> z1_b = 0.0;
    f32<2> z2_b = 0.0;
    f32 b0_c = 1.0;
    f32 b1_c = 0.0;
    f32 b2_c = 0.0;
    f32 a1_c = 0.0;
    f32 a2_c = 0.0;
    f32<2> z1_c = 0.0;
    f32<2> z2_c = 0.0;

    f32 dbgain(f32 v)
    {
        return exp(v * 0.11512925464970229);
    }
    f32 bound(f32 v, f32 lo, f32 hi)
    {
        return fmax(lo, fmin(hi, v));
    }
    f32 tanh_(f32 v)
    {
        f32 e = exp(2.0 * bound(v, -12.0, 12.0));
        return (e - 1.0) / (e + 1.0);
    }
    f32 shape(f32 v, f32 kd)
    {
        f32 r = 0.0;
        if (kd < 0.5)
        {
            r = tanh_(v);
        }
        else
        {
            if (kd < 1.5)
            {
                if (v >= 0.0)
                {
                    r = tanh_(v);
                }
                else
                {
                    r = tanh_(v * 0.7) / 0.7;
                }
            }
            else
            {
                if (kd < 2.5)
                {
                    f32 c = bound(v, -1.0, 1.0);
                    r = 1.5 * c - 0.5 * c * c * c;
                }
                else
                {
                    r = bound(v, -1.0, 1.0);
                }
            }
        }
        return r;
    }

    reset
    {
        runtime_magic = 0;
        p_kind = -1;
    }

    process
    {
        f32 sr = EC.samplerate;
        if (runtime_magic != 715203)
        {
            runtime_magic = 715203;
            wp = 0;
            i32 j = 0;
            while (j < 1024)
            {
                dl[j] = 0.0;
                gt_buf[j] = 1.0;
                j = j + 1;
            }
        }
        if (kind != p_kind)
        {
            p_kind = kind;
            p_k1 = -999.0;
            p_k2 = -999.0;
            p_k3 = -999.0;
            gr_db = 0.0;
            lgain = 1.0;
            z1_a = 0.0;
            z2_a = 0.0;
            z1_b = 0.0;
            z2_b = 0.0;
            z1_c = 0.0;
            z2_c = 0.0;
        }
        f32<> x = in;
        f32<> y = x;
        f32 aux = 0.0;
        f32 pin = fmax(fabs(x[0]), fabs(x[1]));

        // ---- 1: gain, pan, width ----
        if (kind == 1)
        {
            f32 g = (bound(k1, 0.0, 100.0) - 50.0) * 0.48;
            f32 lin = dbgain(g);
            f32 pn = (bound(k2, 0.0, 100.0) - 50.0) * 2.0;
            f32 angle = (pn + 100.0) * 0.00785398163;
            f32 gl = cos(angle) * 1.41421356;
            f32 gr = sin(angle) * 1.41421356;
            f32 wd = bound(k3, 0.0, 100.0) * 0.02;
            f32 mid = (x[0] + x[1]) * 0.5;
            f32 side = (x[0] - x[1]) * 0.5 * wd;
            y = <(mid + side) * lin * gl, (mid - side) * lin * gr>;
        }

        // ---- 2: equaliser, low shelf 100 Hz, bell 1.2 kHz, high shelf 8 kHz ----
        if (kind == 2)
        {
            if (k1 != p_k1 || k2 != p_k2 || k3 != p_k3)
            {
                p_k1 = k1;
                p_k2 = k2;
                p_k3 = k3;
                f32 w0a = 6.283185307 * 100.0 / sr;
                f32 cwa = cos(w0a);
                f32 swa = sin(w0a);
                f32 Aa = exp((bound(k1, 0.0, 100.0) - 50.0) * 0.3 * 0.0575646273);
                f32 al2a = swa * sqrt(Aa) / 0.70710678;
                f32 iaa = 1.0 / ((Aa + 1.0) + (Aa - 1.0) * cwa + al2a);
                b0_a = (Aa * ((Aa + 1.0) - (Aa - 1.0) * cwa + al2a)) * iaa;
                b1_a = (2.0 * Aa * ((Aa - 1.0) - (Aa + 1.0) * cwa)) * iaa;
                b2_a = (Aa * ((Aa + 1.0) - (Aa - 1.0) * cwa - al2a)) * iaa;
                a1_a = (-2.0 * ((Aa - 1.0) + (Aa + 1.0) * cwa)) * iaa;
                a2_a = ((Aa + 1.0) + (Aa - 1.0) * cwa - al2a) * iaa;
                f32 w0b = 6.283185307 * 1200.0 / sr;
                f32 cwb = cos(w0b);
                f32 swb = sin(w0b);
                f32 Ab = exp((bound(k2, 0.0, 100.0) - 50.0) * 0.3 * 0.0575646273);
                f32 alb = swb / (2.0 * 0.9);
                f32 iab = 1.0 / (1.0 + alb / Ab);
                b0_b = (1.0 + alb * Ab) * iab;
                b1_b = (-2.0 * cwb) * iab;
                b2_b = (1.0 - alb * Ab) * iab;
                a1_b = (-2.0 * cwb) * iab;
                a2_b = (1.0 - alb / Ab) * iab;
                f32 w0c = 6.283185307 * 8000.0 / sr;
                f32 cwc = cos(w0c);
                f32 swc = sin(w0c);
                f32 Ac = exp((bound(k3, 0.0, 100.0) - 50.0) * 0.3 * 0.0575646273);
                f32 al2c = swc * sqrt(Ac) / 0.70710678;
                f32 iac = 1.0 / ((Ac + 1.0) - (Ac - 1.0) * cwc + al2c);
                b0_c = (Ac * ((Ac + 1.0) + (Ac - 1.0) * cwc + al2c)) * iac;
                b1_c = (-2.0 * Ac * ((Ac - 1.0) + (Ac + 1.0) * cwc)) * iac;
                b2_c = (Ac * ((Ac + 1.0) + (Ac - 1.0) * cwc - al2c)) * iac;
                a1_c = (2.0 * ((Ac - 1.0) - (Ac + 1.0) * cwc)) * iac;
                a2_c = ((Ac + 1.0) - (Ac - 1.0) * cwc - al2c) * iac;
            }
            f32<> ya = b0_a * x + z1_a;
            z1_a = b1_a * x - a1_a * ya + z2_a;
            z2_a = b2_a * x - a2_a * ya;
            f32<> yb = b0_b * ya + z1_b;
            z1_b = b1_b * ya - a1_b * yb + z2_b;
            z2_b = b2_b * ya - a2_b * yb;
            f32<> yc = b0_c * yb + z1_c;
            z1_c = b1_c * yb - a1_c * yc + z2_c;
            z2_c = b2_c * yb - a2_c * yc;
            y = yc;
        }

        // ---- 3: compressor: threshold, ratio, makeup ----
        if (kind == 3)
        {
            f32 t = -48.0 + bound(k1, 0.0, 100.0) * 0.48;
            f32 rn = bound(k2, 0.0, 100.0) * 0.01;
            f32 c_ratio = 1.0 + 19.0 * rn * rn;
            f32 mk = bound(k3, 0.0, 100.0) * 0.08;
            f32 x_db = 20.0 * log10(fmax(0.000001, pin));
            f32 over = x_db - t;
            f32 gr_target = 0.0;
            if (2.0 * over > 6.0)
            {
                gr_target = (1.0 / c_ratio - 1.0) * over;
            }
            else
            {
                if (2.0 * over > -6.0)
                {
                    f32 k2v = over + 3.0;
                    gr_target = (1.0 / c_ratio - 1.0) * k2v * k2v / 12.0;
                }
            }
            f32 c_att = exp(-1.0 / (0.010 * sr));
            f32 c_rel = exp(-1.0 / (0.120 * sr));
            if (gr_target < gr_db)
            {
                gr_db = c_att * gr_db + (1.0 - c_att) * gr_target;
            }
            else
            {
                gr_db = c_rel * gr_db + (1.0 - c_rel) * gr_target;
            }
            y = x * dbgain(gr_db + mk);
            aux = bound(-gr_db / 24.0, 0.0, 1.0);
        }

        // ---- 4: saturation: drive, type, mix ----
        if (kind == 4)
        {
            f32 dr = bound(k1, 0.0, 100.0) * 0.2;
            f32 dl_ = dbgain(dr);
            f32 ty = floor(bound(k2, 0.0, 99.9) * 0.04);
            f32 m = bound(k3, 0.0, 100.0) * 0.01;
            f32 ol = dbgain(-dr * 0.6);
            f32 sl = shape(x[0] * dl_, ty);
            f32 sr_ = shape(x[1] * dl_, ty);
            y = <(x[0] * (1.0 - m) + sl * m) * ol, (x[1] * (1.0 - m) + sr_ * m) * ol>;
        }

        // ---- 5: limiter: input gain, ceiling, release (2 ms lookahead) ----
        if (kind == 5)
        {
            f32 ig = bound(k1, 0.0, 100.0) * 0.12;
            f32 cn = 1.0 - bound(k2, 0.0, 100.0) * 0.01;
            f32 ceil_db = -12.0 * cn * cn;
            f32 ceil_lin = dbgain(ceil_db);
            f32 rel_ms = 10.0 * exp(bound(k3, 0.0, 100.0) * 0.0391202);
            f32<> xi = x * dbgain(ig);
            f32 pk = fmax(fabs(xi[0]), fabs(xi[1]));
            f32 gt = 1.0;
            if (pk > ceil_lin)
            {
                gt = ceil_lin / pk;
            }
            i32 n = 1;
            f32 nf = floor(0.002 * sr);
            if (nf >= 1.0)
            {
                n = cast(fmin(nf, 1000.0), i32);
            }
            dl[wp] = xi;
            gt_buf[wp] = gt;
            f32 gmin = 1.0;
            i32 kk = 0;
            while (kk < n)
            {
                i32 idx = wp - kk;
                if (idx < 0)
                {
                    idx = idx + 1024;
                }
                gmin = fmin(gmin, gt_buf[idx]);
                kk = kk + 1;
            }
            f32 l_att = exp(-3.0 / cast(n, f32));
            f32 l_rel = exp(-1.0 / (rel_ms * 0.001 * sr));
            if (gmin < lgain)
            {
                lgain = l_att * lgain + (1.0 - l_att) * gmin;
            }
            else
            {
                lgain = l_rel * lgain + (1.0 - l_rel) * gmin;
            }
            i32 rp = wp - n + 1;
            if (rp < 0)
            {
                rp = rp + 1024;
            }
            f32<> d = dl[rp];
            f32<> yl = d * lgain;
            y = <bound(yl[0], -ceil_lin, ceil_lin), bound(yl[1], -ceil_lin, ceil_lin)>;
            wp = wp + 1;
            if (wp >= 1024)
            {
                wp = 0;
            }
            aux = bound(-20.0 * log10(fmax(0.001, lgain)) / 12.0, 0.0, 1.0);
        }

        // ---- 6: utility gain in dB (input / output stages of the strip) ----
        if (kind == 6)
        {
            y = x * dbgain(bound(k1, -24.0, 24.0));
        }

        out = y;
        f32 pout = fmax(fabs(y[0]), fabs(y[1]));
        in_env = fmax(pin, in_env * 0.9995);
        out_env = fmax(pout, out_env * 0.9995);
        f32 ine = bound((20.0 * log10(fmax(0.000001, in_env)) + 60.0) / 66.0, 0.0, 1.0);
        f32 oute = bound((20.0 * log10(fmax(0.000001, out_env)) + 60.0) / 66.0, 0.0, 1.0);
        f32 kd = cast(kind, f32);
        display = <kd * 0.125, ine, oute, aux>;
        display2 = <bound(k1, 0.0, 100.0) * 0.01, bound(k2, 0.0, 100.0) * 0.01, bound(k3, 0.0, 100.0) * 0.01, 0.0>;
    }
}
'''
Path(__file__).with_name("slot.nitro").write_text(NITRO)
