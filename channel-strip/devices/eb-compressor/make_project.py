"""Write bitwig-project.json from spec.py (keeps the control contract in sync)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from spec import SPEC
import meta
controls = []
for d in SPEC["decimals"]:
    controls.append({"parameter": d[1], "widgetClass": 1687, "drawOwners": ["native"], "inputOwner": "native",
                     "knobSize": SPEC.get("knob_size", 3), "gestures": ["drag", "reset"], "defaultNormalized": (d[4] - d[2]) / (d[3] - d[2])})
for c in SPEC["choices"]:
    n = len(c[2])
    controls.append({"parameter": c[1], "widgetClass": 1714, "drawOwners": ["native"], "inputOwner": "native",
                     "gestures": ["select"], "defaultNormalized": c[3] / (n - 1),
                     "statesNormalized": [i / (n - 1) for i in range(n)]})
project = {
    "schemaVersion": 1, "projectId": meta.PROJECT_ID, "name": meta.NAME, "surface": "device",
    "target": {"bitwigVersion": "6.1.3", "platform": "windows-x86_64"},
    "identity": {"uuid": meta.UUID, "creator": "Elodea Blackstar", "category": "Audio FX"},
    "presentation": {"type": "audio-fx", "description": meta.DESCRIPTION},
    "sources": {"nitro": [meta.NITRO], "sksl": ["panel.sksl"]},
    "adapter": {"type": "external-builder", "argv": ["python", "{workspace}/build.py", "--out", "{output}"]},
    "output": {"path": f"build/windows-6.1.3/{meta.NAME}.bwdevice", "libraryPath": f"{meta.NAME}.bwdevice"},
    "preflight": {"profile": "bitwig-6.1.3-hybrid", "expectedNitroInputs": 1 + len(SPEC["decimals"]) + len(SPEC["choices"]),
                  "expectedNitroOutputs": 1 + SPEC.get("vectors", 1), "maxDrawingVectors": SPEC.get("vectors", 1), "requiredAudioInputSourceClassId": 1371,
                  "requiredDelayCompensationInputSourceClassId": 154, "requiredProxyInputCount": 2,
                  "requireSkiaCompiler": True,
                  "controlContract": {"schema": 1, "shaderRole": "non-interactive-display", "controls": controls}},
}
(HERE / "bitwig-project.json").write_text(json.dumps(project, indent=2) + "\n")
overlay = {"extends": "bitwig-project.json", "target": {"bitwigVersion": "6.1.7", "platform": "macos-arm64"},
           "output": {"path": f"build/macos-6.1.7/{meta.NAME}.bwdevice", "libraryPath": f"{meta.NAME}.bwdevice"}}
(HERE / "bitwig-project.macos-6.1.7.json").write_text(json.dumps(overlay, indent=2) + "\n")
