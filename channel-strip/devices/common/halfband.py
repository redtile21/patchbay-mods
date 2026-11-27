"""Nitro code for true 2x oversampling with polyphase IIR half-band filters (after Laurent de Soras' HIIR).

The up/down pair is allpass overall (flat level, 3 to 8 samples of delay, more near the top), so a dry path run
through its own pair stays in phase with the oversampled one. Each chain is one channel (f32); pass ty="f32<2>" for a stereo vector.

    decl("os_in")             -> state declarations (component scope)
    reset("os_in")            -> lines that clear it
    up("os_in", "v")          -> defines f32<> os_in_e, os_in_o (the two oversampled samples, earlier first)
    down("os_out", "a", "b")  -> defines f32<> os_out (back at the base rate)
"""
# design(8, 0.04): 8 coefficients, transition band 0.04 (flat to about 21 kHz at 48 kHz)
COEFS = [0.040633460924, 0.150505129023, 0.300757055992, 0.460774504961,
         0.609524314896, 0.738503841119, 0.849223810392, 0.949742783705]


def decl(p, ty="f32"):
    return "".join(f"    {ty} {p}_x{i} = 0.0;\n    {ty} {p}_y{i} = 0.0;\n" for i in range(len(COEFS)))


def reset(p, indent="        "):
    return "".join(f"{indent}{p}_x{i} = 0.0;\n{indent}{p}_y{i} = 0.0;\n" for i in range(len(COEFS)))


def _chain(p, a, b, indent, ty):
    out = []
    for i in range(0, len(COEFS), 2):
        for k, var in ((i, a), (i + 1, b)):
            out.append(f"{indent}{ty} {p}_t{k} = ({var} - {p}_y{k}) * {COEFS[k]} + {p}_x{k};\n"
                       f"{indent}{p}_x{k} = {var};\n{indent}{p}_y{k} = {p}_t{k};\n{indent}{var} = {p}_t{k};\n")
    return "".join(out)


def up(p, v, indent="        ", ty="f32"):
    """Defines {p}_e and {p}_o: the two oversampled samples for input v, earlier first."""
    return f"{indent}{ty} {p}_e = {v};\n{indent}{ty} {p}_o = {v};\n" + _chain(p, f"{p}_e", f"{p}_o", indent, ty)


def down(p, a, b, indent="        ", ty="f32"):
    """Defines {p}: one base-rate sample from the oversampled pair a (earlier), b."""
    return (f"{indent}{ty} {p}_s0 = {b};\n{indent}{ty} {p}_s1 = {a};\n" + _chain(p, f"{p}_s0", f"{p}_s1", indent, ty)
            + f"{indent}{ty} {p} = 0.5 * ({p}_s0 + {p}_s1);\n")
