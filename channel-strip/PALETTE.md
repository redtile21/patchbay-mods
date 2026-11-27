# Elodea Blackstar palette

Shared by every shader-drawn display (units and strip). Colours are linear 0..1 RGB as written in SkSL.

| Role | Value |
| --- | --- |
| Panel face | `.060, .070, .082` |
| Meter well / darkest | `.030, .036, .043` |
| Grid lines | `.105, .125, .145` |
| Accent (signal, curves) | `.33, .60, .96` |
| Text | `.82, .86, .90` |
| Inactive / thru | `.21, .24, .28` |
| Warning / gain reduction | `.95, .42, .26` |
| Meter ramp | green `.24, .62, .17` to amber `.96, .56, .12`, red `.92, .30, .22` near the top |

Native Bitwig widgets (knobs, dropdowns) keep the host theme; only drawn displays use this palette.
