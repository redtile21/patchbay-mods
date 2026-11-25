"""Compile the gain stage and write the EB Strip Spike container."""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

import compiler_profiles
import project_contracts
from strip_document import document
from devices.common.document_graph import run


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--compiler-inputs", type=Path, required=True)
    cli.add_argument("--out", type=Path)
    cli.add_argument("--project-file", type=Path, default=HERE / "bitwig-project.json")
    args = cli.parse_args()
    project = project_contracts.load(args.project_file.resolve())
    inputs, profile = compiler_profiles.validate_inputs(args.compiler_inputs)
    compiler_profiles.require_target(profile, project["target"])
    codec, _ = compiler_profiles.document_parser(inputs, profile)
    output = (args.out or HERE / project["output"]["path"]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    nitro, tap_nitro, meter_nitro = project["sources"]["nitro"]
    shader = (HERE / project["sources"]["sksl"][0]).read_text(encoding="utf-8")
    meter_shader = (HERE / project["sources"]["sksl"][1]).read_text(encoding="utf-8")
    backdrop_shader = (HERE / project["sources"]["sksl"][2]).read_text(encoding="utf-8")
    with TemporaryDirectory(prefix="eb-strip-", dir=output.parent) as temporary:
        staging = Path(temporary)
        compiled = staging / "stage.nitrobin"
        compiler_profiles.compile_source(HERE / nitro, compiled, args.compiler_inputs)
        meter_compiled = staging / "meter.nitrobin"
        compiler_profiles.compile_source(HERE / meter_nitro, meter_compiled, args.compiler_inputs)
        tap_compiled = staging / "tap.nitrobin"
        compiler_profiles.compile_source(HERE / tap_nitro, tap_compiled, args.compiler_inputs)
        # Character: one source, two builds (the input copy has an on/off switch, the output copy is always on)
        char_src = (HERE / "character.nitro").read_text(encoding="utf-8")
        char_bins = []
        for name, text in (("char_in", char_src), ("char_out", char_src.replace("    value_inport bool enabled;\n", "").replace(" && enabled", ""))):
            (staging / f"{name}.nitro").write_text(text, encoding="utf-8")
            compiler_profiles.compile_source(staging / f"{name}.nitro", staging / f"{name}.nitrobin", args.compiler_inputs)
            char_bins.append((staging / f"{name}.nitrobin").read_bytes())
        source = staging / "device.json"
        source.write_text(json.dumps(document(project, compiled.read_bytes(), tap_compiled.read_bytes(), meter_compiled.read_bytes(), shader, meter_shader, backdrop_shader, char_bins), ensure_ascii=False), encoding="utf-8")
        candidate = staging / output.name
        run([str(codec), "from-json", str(source), str(candidate)])
        candidate.replace(output)
    print(f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
