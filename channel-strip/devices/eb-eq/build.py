"""Compile the Nitro source and write the device (generic EB unit)."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "scripts"), str(ROOT / "devices" / "eb-unit")]

import compiler_profiles, project_contracts
from spec import SPEC
from unit_document2 import document
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
    nitro, = project["sources"]["nitro"]
    sksl = (project["sources"]["sksl"] or [None])[0]
    with TemporaryDirectory(prefix="eb-unit-", dir=output.parent) as temporary:
        staging = Path(temporary)
        compiled = staging / "unit.nitrobin"
        compiler_profiles.compile_source(HERE / nitro, compiled, args.compiler_inputs)
        source = staging / "device.json"
        source.write_text(json.dumps(document(SPEC, project, compiled.read_bytes(),
                          (HERE / sksl).read_text(encoding="utf-8") if sksl else ""), ensure_ascii=False), encoding="utf-8")
        candidate = staging / output.name
        run([str(codec), "from-json", str(source), str(candidate)])
        candidate.replace(output)
    print(f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
