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
    nitro, = project["sources"]["nitro"]
    with TemporaryDirectory(prefix="eb-strip-", dir=output.parent) as temporary:
        staging = Path(temporary)
        compiled = staging / "stage.nitrobin"
        compiler_profiles.compile_source(HERE / nitro, compiled, args.compiler_inputs)
        source = staging / "device.json"
        source.write_text(json.dumps(document(project, compiled.read_bytes()), ensure_ascii=False), encoding="utf-8")
        candidate = staging / output.name
        run([str(codec), "from-json", str(source), str(candidate)])
        candidate.replace(output)
    print(f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
