"""Speckled-metal background texture as a panel image item (class 1719, an SVG holding a JPEG).

The source photo is rotated to landscape, scaled, mirror-tiled to cover any panel and darkened, then cropped to the panel.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image

from devices.common.panel_helpers import grid_layout, obj, value as v

SOURCE = Path(__file__).with_name("texture-source.jpg")
PX_PER_UNIT = 12            # image pixels per grid unit (the item stretches the picture to its rectangle)
SOURCE_SCALE = 0.5          # speckles stay this fraction of their size in the photo
DARKEN = 0.62               # multiplier on the photo's grey (the plate sits behind light-blue readouts)
BLUE_TINT = (0.97, 1.0, 1.04)


def _master():
    im = Image.open(SOURCE).convert("L").transpose(Image.Transpose.ROTATE_90)
    im = im.resize((int(im.width * SOURCE_SCALE), int(im.height * SOURCE_SCALE)), Image.Resampling.LANCZOS)
    w, h = im.size
    big = Image.new("L", (w * 2, h * 2))
    big.paste(im, (0, 0))
    big.paste(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (w, 0))
    big.paste(im.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (0, h))
    big.paste(im.transpose(Image.Transpose.ROTATE_180), (w, h))
    return big


def jpeg_bytes(width_units, height_units, offset=(0, 0)):
    m = _master()
    w, h = int(width_units * PX_PER_UNIT), int(height_units * PX_PER_UNIT)
    ox, oy = offset
    assert ox + w <= m.width and oy + h <= m.height, (m.size, w, h)
    crop = m.crop((ox, oy, ox + w, oy + h)).point(lambda p: int(p * DARKEN))
    rgb = Image.merge("RGB", [crop.point(lambda p, t=t: min(255, int(p * t))) for t in BLUE_TINT])
    buf = io.BytesIO()
    rgb.save(buf, "JPEG", quality=82, optimize=True)
    return buf.getvalue()


def svg(width_units, height_units, offset=(0, 0)):
    uri = "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes(width_units, height_units, offset)).decode()
    pw, ph = int(width_units * PX_PER_UNIT), int(height_units * PX_PER_UNIT)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{pw}" height="{ph}" '
            f'viewBox="0 0 {pw} {ph}"><image x="0" y="0" width="{pw}" height="{ph}" href="{uri}" xlink:href="{uri}"/></svg>')


def image_item(x, y, width, height, svg_text):
    return obj(1719, "image_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, width, height)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "filename#6258": v("String", ""),
        "svg_data#6259": v("String", svg_text), "color#6521": v("Int16", 1000),
        "scale#6767": v("Double", 1.0), "opacity#6768": v("Double", 1.0)})


def background_item(width_units, height_units, offset=(0, 0)):
    return image_item(0, 0, width_units, height_units, svg(width_units, height_units, offset))
