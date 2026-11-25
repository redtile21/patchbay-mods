"""Narrow geometric capitals and figures (after Twentieth Century / Futura Condensed) for the SkSL displays.

Each glyph is a set of strokes in a 1 x 2 box (x right, y down, cap height 0.06 .. 1.94). Curves are flattened into
segments; `sksl()` writes the `letter(q, c)` (A = 1 .. Z = 26) and `digit(q, d)` functions the shaders use, and
`splice(text)` swaps them into a shader source. `python -m devices.common.glyphs preview.png` renders a proof.
"""
from __future__ import annotations

import math
import re

T, B, M = 0.06, 1.94, 1.0
L, R = 0.20, 0.80
RX = (R - L) / 2            # round letters: elliptical caps on straight sides
RY = 0.40
CX = 0.5
CYT, CYB = T + RY, B - RY
HALF = (0.075, 0.135)       # smoothstep edges of the stroke (half width about .105 of the glyph width)


def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(3, int(abs(a1 - a0) / 12))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


OX, OY = RX + .04, (B - T) / 2     # true ovals for O C G Q D 0, a little wider than the straight letters


def oval():
    return arc(CX, M, OX, OY, 0, 360, 36)


GLYPHS = {
    "A": [[(L - .03, B), (CX, T - .03), (R + .03, B)], [(L + .12, 1.38), (R - .12, 1.38)]],
    "B": [[(L, B), (L, T), (.50, T)] + arc(.50, (T + M) / 2, .26, (M - T) / 2, -90, 90) + [(L, M)],
          [(L, M), (.52, M)] + arc(.52, (M + B) / 2, .28, (B - M) / 2, -90, 90) + [(L, B)]],
    "C": [arc(CX, M, OX, OY, -42, -318, 30)],
    "D": [[(L, T), (.36, T)] + arc(.36, M, R + .02 - .36, OY, -90, 90, 24) + [(L, B), (L, T)]],
    "E": [[(R - .04, T), (L, T), (L, B), (R - .04, B)], [(L, M), (R - .10, M)]],
    "F": [[(R - .04, T), (L, T), (L, B)], [(L, M), (R - .10, M)]],
    "G": [arc(CX, M, OX, OY, -42, -360, 34) + [(CX + OX, 1.08)], [(.54, 1.08), (CX + OX, 1.08)]],
    "H": [[(L, T), (L, B)], [(R, T), (R, B)], [(L, M), (R, M)]],
    "I": [[(CX, T), (CX, B)]],
    "J": [[(R - .06, T)] + arc(R - .06 - .27, CYB, .27, RY, 0, 160)],
    "K": [[(L, T), (L, B)], [(R + .02, T), (L, 1.20)], [(L + .17, .97), (R + .03, B)]],
    "L": [[(L, T), (L, B), (R - .04, B)]],
    "M": [[(L - .07, B), (L, T), (CX, 1.82), (R, T), (R + .07, B)]],
    "N": [[(L, B), (L, T - .02), (R, B + .02), (R, T)]],
    "O": [oval()],
    "P": [[(L, B), (L, T), (.48, T)] + arc(.48, (T + 1.08) / 2, R - .48, (1.08 - T) / 2, -90, 90) + [(L, 1.08)]],
    "Q": [oval(), [(.56, 1.50), (R + .08, B + .06)]],
    "R": [[(L, B), (L, T), (.48, T)] + arc(.48, (T + 1.08) / 2, R - .48, (1.08 - T) / 2, -90, 90) + [(L, 1.08)],
          [(.46, 1.08), (R + .02, B)]],
    "S": [arc(CX, .50, .28, .44, -25, -270) + arc(CX, 1.45, .31, .49, -90, 155)],
    "T": [[(L - .05, T), (R + .05, T)], [(CX, T), (CX, B)]],
    "U": [[(L, T)] + arc(CX, CYB, RX, RY, 180, 0) + [(R, T)]],
    "V": [[(L - .05, T), (CX, B + .03), (R + .05, T)]],
    "W": [[(L - .12, T), (L + .07, B), (CX, T), (R - .07, B), (R + .12, T)]],
    "X": [[(L, T), (R, B)], [(R, T), (L, B)]],
    "Y": [[(L - .03, T), (CX, 1.02), (R + .03, T)], [(CX, 1.02), (CX, B)]],
    "Z": [[(L, T), (R, T), (L, B), (R, B)]],
}

DIGITS = {
    0: [oval()],
    1: [[(.28, .40), (.56, T), (.56, B)]],
    2: [arc(CX, .50, .29, .44, 200, 380) + [(L, B), (R + .02, B)]],
    3: [arc(CX, .49, .27, .42, 205, 450) + [(.44, .91)], arc(CX, 1.43, .31, .51, -90, 160)],
    4: [[(.62, B), (.62, T), (L - .04, 1.42), (R + .05, 1.42)]],
    5: [[(R - .02, T), (L + .04, T), (L + .01, .98)] + arc(CX, 1.43, .31, .51, -122, 160)],
    6: [[(.68, T), (L + .03, 1.30)], arc(CX, 1.44, .31, .50, 0, 360, 30)],
    7: [[(L - .02, T), (R + .02, T), (.36, B)]],
    8: [arc(CX, .50, .26, .44, 0, 360, 30), arc(CX, 1.45, .31, .49, 0, 360, 30)],
    9: [arc(CX, .56, .31, .50, 0, 360, 30), [(R - .02, .70), (.32, B)]],
}


def segments(strokes):
    out = []
    for path in strokes:
        for (a, b) in zip(path, path[1:]):
            if math.dist(a, b) > 1e-4:
                out.append((a, b))
    return out


def _bounds(segs):
    xs = [c for s in segs for c in (s[0][0], s[1][0])]
    ys = [c for s in segs for c in (s[0][1], s[1][1])]
    return min(xs), min(ys), max(xs), max(ys)


def _branch(segs, pad=.16):
    x0, y0, x1, y1 = _bounds(segs)
    lines = [f"        if (q.x < {x0 - pad:.3f} || q.x > {x1 + pad:.3f} || q.y < {y0 - pad:.3f} || q.y > {y1 + pad:.3f}) return 0.;"]
    for (a, b) in segs:
        lines.append(f"        m = min(m, sdseg(q, float2({a[0]:.3f}, {a[1]:.3f}), float2({b[0]:.3f}, {b[1]:.3f})));")
    return "\n".join(lines)


def _func(name, arg, table, lead):
    parts = [lead, f"float {name}(float2 q, float {arg}) {{",
             f"    if ({arg} < {'.5' if name == 'letter' else '0.'}) return 0.;", "    float m = 10.;"]
    first = True
    for code, strokes in table:
        cond = f"{arg} > {code - .5:.1f} && {arg} < {code + .5:.1f}"
        parts.append(f"    {'if' if first else 'else if'} ({cond}) {{")
        parts.append(_branch(segments(strokes)))
        parts.append("    }")
        first = False
    parts.append(f"    return 1. - smoothstep({HALF[0]}, {HALF[1]}, m);")
    parts.append("}")
    return "\n".join(parts)


def letter_sksl():
    table = [(ord(ch) - 64, s) for ch, s in GLYPHS.items()]
    return _func("letter", "c", table, "// Narrow geometric capital (after Twentieth Century) in a 1 x 2 box; c is 1 for A to 26 for Z, 0 draws nothing.")


def digit_sksl():
    return _func("digit", "d", sorted(DIGITS.items()), "// Narrow geometric figure (after Twentieth Century) in a 1 x 2 box; d < 0 draws nothing.")


def _replace_func(text, name, new):
    m = re.search(rf"(//[^\n]*\n)?float {name}\(float2 q, float \w\) \{{\n", text)
    if not m:
        return text
    depth, i = 0, m.end() - 1
    while True:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return text[:m.start()] + new + text[i + 1:]


def splice(text):
    text = _replace_func(text, "letter", letter_sksl())
    text = _replace_func(text, "digit", digit_sksl())
    return text


def render(segs_by_glyph, h, gap=1.0):
    """Proof render with the shader's own maths (numpy)."""
    import numpy as np
    w = h * .5
    adv = w * gap
    W = int(adv * len(segs_by_glyph) + w) + 4
    H = int(h + 6)
    yy, xx = np.mgrid[0:H, 0:W].astype(float) + .5
    img = np.zeros((H, W))
    for k, segs in enumerate(segs_by_glyph):
        qx, qy = (xx - 2 - k * adv) / w, (yy - 3) / w
        m = np.full_like(qx, 10.)
        for (a, b) in segs:
            px, py = qx - a[0], qy - a[1]
            bx, by = b[0] - a[0], b[1] - a[1]
            t = np.clip((px * bx + py * by) / (bx * bx + by * by), 0, 1)
            m = np.minimum(m, np.hypot(px - bx * t, py - by * t))
        e0, e1 = HALF
        t = np.clip((m - e0) / (e1 - e0), 0, 1)
        img = np.maximum(img, 1 - t * t * (3 - 2 * t))
    return img


if __name__ == "__main__":
    import sys
    import numpy as np
    from PIL import Image
    rows = []
    for h in (14, 22, 60):
        rows.append(render([segments(GLYPHS[c]) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"], h, 1.08))
        rows.append(render([segments(DIGITS[d]) for d in range(10)] + [segments(GLYPHS[c]) for c in "GAINEQLPFHPFENHTHRU"], h, 1.08))
    W = max(r.shape[1] for r in rows)
    canvas = np.vstack([np.pad(r, ((2, 2), (0, W - r.shape[1]))) for r in rows])
    bg = np.array([.082, .087, .096])
    fg = np.array([.42, .74, .95])
    rgb = bg + canvas[..., None] * (fg - bg)
    Image.fromarray((rgb * 255).astype(np.uint8)).save(sys.argv[1] if len(sys.argv) > 1 else "glyphs.png")
