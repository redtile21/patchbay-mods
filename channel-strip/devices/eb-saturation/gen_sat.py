"""Generate saturation.nitro (left and right channels share one template)."""
from pathlib import Path

chan = '''
        // ---- channel {c} ----
        f32 d_{c} = x[{i}] * drive_lin + bias_v;
        f32 s_{c} = shape(d_{c}, kind) - bias_off;
        if (os == 1)
        {{
            f32 mid_{c} = (d_{c} + prev_{c}) * 0.5;
            s_{c} = (s_{c} + shape(mid_{c}, kind) - bias_off) * 0.5;
        }}
        prev_{c} = d_{c};
        // tone: tilt around 1 kHz
        lp_{c} = lp_{c} + tone_a * (s_{c} - lp_{c});
        f32 t_{c} = lp_{c} * tone_lo + (s_{c} - lp_{c}) * tone_hi;
        f32 o_{c} = (x[{i}] * (1.0 - m) + t_{c} * m) * out_lin;
'''
src = '''component eb_saturation
{
    audio_inport in;
    audio_inport f32 drive = 0.0;
    audio_inport f32 bias = 0.0;
    audio_inport f32 tone = 0.0;
    audio_inport f32 mix = 100.0;
    audio_inport f32 output = 0.0;
    value_inport i32 sat_type;
    value_inport i32 auto_gain;
    value_inport i32 oversampling;

    audio_outport out;
    audio_outport f32<4> display;
    audio_outport f32<4> display2;

    f32 prev_l = 0.0;
    f32 prev_r = 0.0;
    f32 lp_l = 0.0;
    f32 lp_r = 0.0;
    f32 meter_l = 0.0;
    f32 meter_r = 0.0;
    f32 in_env = 0.0;
    f32 in_pk = 0.0;
    f32 out_pk = 0.0;
    f32 t_in = 0.0;
    f32 t_out = 0.0;

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
    f32 shape(f32 v, f32 kind)
    {
        f32 r = 0.0;
        if (kind < 0.5)
        {
            r = tanh_(v);
        }
        else
        {
            if (kind < 1.5)
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
                if (kind < 2.5)
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
        prev_l = 0.0;
        prev_r = 0.0;
        lp_l = 0.0;
        lp_r = 0.0;
        meter_l = 0.0;
        meter_r = 0.0;
        in_env = 0.0;
        in_pk = 0.0;
        out_pk = 0.0;
        t_in = 0.0;
        t_out = 0.0;
    }

    process
    {
        f32<> x = in;
        f32 sr = EC.samplerate;
        f32 dr = bound(drive, 0.0, 36.0);
        f32 drive_lin = dbgain(dr);
        f32 kind = cast(sat_type, f32);
        f32 bias_v = bound(bias, -1.0, 1.0) * 0.5;
        f32 bias_off = shape(bias_v, kind);
        f32 tn = bound(tone, -6.0, 6.0);
        f32 tone_lo = dbgain(-tn * 0.5);
        f32 tone_hi = dbgain(tn * 0.5);
        f32 tone_a = 1.0 - exp(-6.283185307 * 1000.0 / sr);
        f32 m = bound(mix, 0.0, 100.0) * 0.01;
        f32 ag = 0.0;
        if (auto_gain == 1)
        {
            ag = -dr * 0.6;
        }
        f32 out_lin = dbgain(bound(output, -24.0, 6.0) + ag);
        i32 os = oversampling;
''' + chan.format(c="l", i=0) + chan.format(c="r", i=1) + '''
        f32<> y = <o_l, o_r>;
        out = y;
        meter_l = fmax(fabs(o_l), meter_l * 0.999);
        meter_r = fmax(fabs(o_r), meter_r * 0.999);
        f32 pin = fmax(fabs(x[0]), fabs(x[1]));
        f32 pout = fmax(fabs(o_l), fabs(o_r));
        in_env = fmax(pin, in_env * 0.999);
        f32 hold_len = 5.0 * sr;
        if (pin >= in_pk)
        {
            in_pk = pin;
            t_in = 0.0;
        }
        else
        {
            t_in = t_in + 1.0;
            if (t_in > hold_len)
            {
                in_pk = pin;
                t_in = 0.0;
            }
        }
        if (pout >= out_pk)
        {
            out_pk = pout;
            t_out = 0.0;
        }
        else
        {
            t_out = t_out + 1.0;
            if (t_out > hold_len)
            {
                out_pk = pout;
                t_out = 0.0;
            }
        }
        f32 ine = bound((20.0 * log10(fmax(0.000001, in_env)) + 60.0) / 66.0, 0.0, 1.0);
        f32 oute = bound((20.0 * log10(fmax(0.000001, fmax(meter_l, meter_r))) + 60.0) / 66.0, 0.0, 1.0);
        f32 inp = bound((20.0 * log10(fmax(0.000001, in_pk)) + 60.0) / 66.0, 0.0, 1.0);
        f32 outp = bound((20.0 * log10(fmax(0.000001, out_pk)) + 60.0) / 66.0, 0.0, 1.0);
        // Type and mix share a lane: floor(lane * 4) = type, fract(lane * 4) = mix.
        f32 tm = (kind + m * 0.99) / 4.0;
        display = <dr / 36.0, (bound(bias, -1.0, 1.0) + 1.0) * 0.5, tm, ine>;
        display2 = <oute, inp, outp, 0.0>;
    }
}
'''
Path(__file__).with_name("saturation.nitro").write_text(src)
