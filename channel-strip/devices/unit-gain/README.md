# EB Gain (Spike C)

Sources only. The builder is the `devices/eb-gain` workspace in a checkout of
polarity/bitwig-devices-blueprint (see `../../DESIGN.md` §8): copy these four files into it, add
`build.py` and `demo_document.py` adapted from `devices/blueprint-gain`, and build with the
`macos-arm64-bitwig-6.1.7` profile.

Spike scope: three decimal parameters (Gain dB, Pan, Width), three quick-control knobs and a
stereo level display. Not yet covered: Polarity and Mono (need a choice or toggle atom, which
the blueprint has no template for), peak hold (needs Nitro state) and latency reporting.
