# EB BlackStrip

A channel strip for Bitwig Studio made of native (Nitro) devices, with the companion mod EB Strip Console.

- **User guide** (also shipped in both release ZIPs): [mod/README.md](mod/README.md)
- **Releases**: [releases/](releases)
- **Roadmap and design notes**: [ROADMAP.md](ROADMAP.md), [DESIGN.md](DESIGN.md), [PALETTE.md](PALETTE.md)
- **How it was built, and what to watch for if you build something similar**:
  [../docs/building-bitwig-devices-and-mods.md](../docs/building-bitwig-devices-and-mods.md)

Layout: `devices/` holds the device sources (built with
[bitwig-devices-blueprint](https://github.com/polarity/bitwig-devices-blueprint)), `mod/` the mod (`build.sh`,
`release.sh`), `help/help_text.py` the F1 help text, `presets/` the presets and their generator.
