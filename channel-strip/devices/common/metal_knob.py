"""Metallic knob caps drawn over Bitwig's native knobs (panel image items, class 1719).

The native knob stays underneath and keeps all interaction (images take no clicks); a brushed-steel cap hides its dark
cap and white pointer. The pointer is one small SVG per step, each shown by a panel expression on the knob's value
(expressions run in the interface, so they follow the knob while the device is bypassed).
"""
from __future__ import annotations

import base64
import io
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageFilter

from devices.common.panel_helpers import grid_layout, obj, value as v

PX = 16                 # image pixels per grid unit
STEPS = 35              # pointer positions (odd: a step sits on the centre)
SWEEP = 270.0
POINTER = "#15191e"


@lru_cache(maxsize=None)
def cap_png(r_units):
    """Brushed steel cap with a knurled edge and a soft shadow; returns (png bytes, margin in units)."""
    margin = 0.7
    n = int(math.ceil((r_units + margin) * 2 * PX))
    ss = 3
    N = n * ss
    c = (N - 1) / 2.0
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float64)
    dx, dy = (xx - c) / (PX * ss), (yy - c) / (PX * ss)
    d = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    rho = d / r_units
    rng = np.random.default_rng(7)
    rings = rng.normal(0, 1, 400)
    ring = rings[np.clip((d * PX * ss / 1.6).astype(int), 0, 399)]
    # top face: brushed concentric grooves under a two-lobed anisotropic highlight
    lobe = np.cos(2 * (th - 0.9))
    face = 0.50 + 0.30 * lobe + 0.045 * ring - 0.10 * np.clip((rho - 0.5) / 0.3, 0, 1) ** 2
    # knurled edge: ridges around the rim, lit like the face
    rim_pos = np.clip((rho - 0.84) / 0.16, 0, 1)
    ridge = np.cos(th * 64)
    rim = 0.46 + 0.24 * np.cos(th - 0.9) + 0.16 * ridge * (0.6 + 0.4 * np.cos(th - 0.9)) - 0.28 * np.clip((rim_pos - 0.82) / 0.18, 0, 1)
    # chamfer between face and rim: bright where it faces the light, dark opposite
    cham = 0.50 + 0.42 * np.cos(th + 0.9 + math.pi)
    b = np.where(rho < 0.80, face, np.where(rho < 0.84, cham, rim))
    lum = np.clip(0.16 + 0.78 * b, 0, 1)
    tint = np.array([0.96, 1.0, 1.06])
    rgb = np.clip(lum[..., None] * tint, 0, 1)
    edge = np.clip((1.0 - rho) * r_units * PX * ss / 1.4 + 0.5, 0, 1)         # anti-aliased disc edge
    alpha = edge
    # shadow: the disc, shifted down a little and blurred, under the cap
    sh = Image.fromarray((np.where(np.hypot(dx, dy - 0.10) < r_units * 1.02, 255, 0)).astype(np.uint8)).resize((n, n), Image.Resampling.BOX)
    sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(PX * 0.16)), dtype=np.float64) / 255.0 * 0.55
    cap_rgb = np.asarray(Image.fromarray((rgb * 255).astype(np.uint8)).resize((n, n), Image.Resampling.BOX), dtype=np.float64) / 255.0
    cap_a = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((n, n), Image.Resampling.BOX), dtype=np.float64) / 255.0
    out_a = cap_a + sh * (1 - cap_a)
    out_rgb = np.where(out_a[..., None] > 1e-4, (cap_rgb * cap_a[..., None]) / np.maximum(out_a[..., None], 1e-4), 0.0)
    img = np.dstack([out_rgb, out_a])
    buf = io.BytesIO()
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGBA").save(buf, "PNG", optimize=True)
    return buf.getvalue(), margin


def _wrap(w_units, h_units, inner):
    pw, ph = int(w_units * PX), int(h_units * PX)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{pw}" height="{ph}" '
            f'viewBox="0 0 {pw} {ph}">{inner}</svg>')


def cap_svg(w_units, h_units, cx, cy, r):
    png, margin = cap_png(round(r, 3))
    uri = "data:image/png;base64," + base64.b64encode(png).decode()
    side = 2 * (r + margin) * PX
    x, y = cx * PX - side / 2, cy * PX - side / 2
    return _wrap(w_units, h_units, f'<image x="{x:.2f}" y="{y:.2f}" width="{side:.2f}" height="{side:.2f}" href="{uri}" xlink:href="{uri}"/>')


def pointer_svg(w_units, h_units, cx, cy, r, step):
    a = math.radians(-SWEEP / 2 + SWEEP * step / (STEPS - 1))
    sx, sy = math.sin(a), -math.cos(a)
    r0, r1 = 0.30 * r, 0.80 * r
    x0, y0, x1, y1 = (cx + r0 * sx) * PX, (cy + r0 * sy) * PX, (cx + r1 * sx) * PX, (cy + r1 * sy) * PX
    wd = 0.30 * PX
    return _wrap(w_units, h_units,
                 f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{POINTER}" stroke-width="{wd:.2f}" stroke-linecap="round"/>')


def image_item(x, y, w, h, svg, visible=True):
    return obj(1719, "image_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", visible), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "filename#6258": v("String", ""),
        "svg_data#6259": v("String", svg), "color#6521": v("Int16", 1000),
        "scale#6767": v("Double", 1.0), "opacity#6768": v("Double", 1.0)})


def _num(x):
    return f"{x:.6f}".rstrip("0").rstrip(".")


def step_rule(ident, lo, hi, j):
    """Panel expression true while the knob's value is nearest step j. A rule can't read negative decimals, so a
    range below zero is shifted to start at zero."""
    shift = -lo if lo < 0 else 0.0
    expr = f"{ident}+{_num(shift)}" if shift else ident
    a0 = lo + shift
    span = hi - lo
    n = STEPS - 1
    a, b = a0 + span * (j - .5) / n, a0 + span * (j + .5) / n
    if j == 0:
        return f"{expr}<{_num(b)}"
    if j == n:
        return f"{expr}>={_num(a)}"
    return f"{expr}>={_num(a)} && {expr}<{_num(b)}"


def knob_overlay(rect, centre, r, ident, lo, hi):
    """rect = (x, y, w, h) of the native knob's panel item; centre = (cx, cy) of its cap inside that rect, in units.
    Returns (items, [(expression, item)]): the cap first, then one pointer item per step."""
    x, y, w, h = rect
    cx, cy = centre
    items = [image_item(x, y, w, h, cap_svg(w, h, cx, cy, r))]
    rules = []
    for j in range(STEPS):
        it = image_item(x, y, w, h, pointer_svg(w, h, cx, cy, r, j), visible=False)
        items.append(it)
        rules.append((step_rule(ident, lo, hi, j), it))
    return items, rules
