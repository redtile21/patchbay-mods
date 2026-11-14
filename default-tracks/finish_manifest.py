import json, re, sys
src, hooks_path, out = sys.argv[1:4]
m = json.load(open(src)); h = json.load(open(hooks_path))
targets = m.setdefault("targets", {}); m.setdefault("hooks", [])
def tid(t):
    for k, v in targets.items():
        if v == t: return k
    base = t["class"] if t["kind"] == "class" else t["owner"] + "." + t["name"]
    base = re.sub(r"[^A-Za-z0-9_.-]", "", base.replace("/", ".").replace("$", "_").replace("<init>", "init"))
    k, n = base, 2
    while k in targets: k = f"{base}-{n}"; n += 1
    targets[k] = t; return k
for x in h.get("hooks", []):
    e = {"id": x["id"], "target": tid(x["target"]), "transform": x["transform"]}
    if "method_from" in x:
        e["method"] = {"from_target": tid(x["method_from"])}; e["body"] = {"template": x["body"]}
    if "match" in x:
        mt = x["match"]
        e["match"] = {"opcode": mt["opcode"], "target": tid(mt["target"]), "occurrence": mt["occurrence"]} if "target" in mt else dict(mt)
    e["bridge"] = x["bridge"]
    m["hooks"].append(e)
if h.get("hook_classes"): m["helper"] = {"jar": "helper.jar", "class": h["hook_classes"][0]}
opens = sorted(tid(a) for a in h.get("access", []))
if opens: m["opens"] = opens
json.dump(m, open(out, "w"), indent=2)
