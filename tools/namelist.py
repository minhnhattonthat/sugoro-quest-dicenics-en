"""Names + menu labels translation batch.
    python -X utf8 tools/namelist.py split            # work/tl/names.tsv
    python -X utf8 tools/namelist.py check [FILE]     # work/tl/names.out.tsv: OK or errors
    python -X utf8 tools/namelist.py merge [FILE]     # check, then write en into script/names.json + labels.json
Ids: N04_92A3 (name string, script/names.json) or L012 (label-only entry, script/labels.json).
A name that is also a label (labels.json "name") is drawn twice: in text (main font) and as a 64 px label (tiny
font); its English must fit both.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import labels  # noqa: E402
import lint  # noqa: E402
import names  # noqa: E402

TL = ROOT / "work" / "tl"
LABELS = ROOT / "script/labels.json"
KIND = {0x21DB4: "character/stat dice", 0x21708: "item/spell", 0x333F0: "key item", 0x40AE3: "weapon/armour",
        0x40C87: "monster"}
ACTOR_PX, ITEM_PX = lint.BATTLE_ACTOR_PX, lint.VAR_PX_ITEM   # the lint budgets for {v} inserts


def kind(e):
    for first, n, stride in [(s[1], s[2], s[3]) for s in names.SLOTS]:
        if any(first <= s < first + n * stride for s in e["slots"]):
            return KIND[first]
    return "?"


def load_labels():
    return json.loads(LABELS.read_text(encoding="utf-8"))


def rows():
    """[(id, kind, limit, jp)]"""
    lab = load_labels()
    labelled = {e["name"] for e in lab if e["name"]}
    out = []
    for e in names.load():
        k = kind(e)
        px = ACTOR_PX if k in ("monster", "character/stat dice") else ITEM_PX
        lim = f"{px}px" + ("+label64" if e["id"] in labelled else "")
        out.append((e["id"], k, lim, e["jp"]))
    for e in lab:
        if e["jp"] and not e["name"]:
            out.append((f"L{e['idx']:03d}", "menu label", "label64", e["jp"]))
    return out


def problems(rid, lim, en):
    errs = []
    if not en.strip():
        return ["empty"]
    if any(ord(c) > 126 for c in en) or set(en) & set(";*<>@{}\\\t"):
        errs.append("non-ASCII or banned character")
        return errs
    if rid.startswith("N"):
        try:
            b = lint.EN.encode(en)
        except Exception as x:  # noqa: BLE001
            return [f"not encodable: {x}"]
        if len(b) > names.MAX_BYTES:
            errs.append(f"{len(b)} bytes > {names.MAX_BYTES}")
        px = lint.line_px(en)
        limit = int(lim.split("px")[0])
        if px > limit:
            errs.append(f"{px}px > {limit}px in text")
    if "label64" in lim:
        try:
            w = labels.text_width(en)
            if w > labels.WIDTH:
                errs.append(f"label {w}px > 64px")
        except KeyError as x:
            errs.append(f"label font lacks {x}")
    return errs


def read_out(path):
    out = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            i, en = line.split("\t", 1)
            out[i] = en.rstrip()
    return out


def check(path):
    rs = {r[0]: r for r in rows()}
    out = read_out(path)
    errs = [f"{i}: missing" for i in rs if i not in out] + [f"{i}: unknown id" for i in out if i not in rs]
    for i, en in out.items():
        if i in rs:
            errs += [f"{i}: {p}" for p in problems(i, rs[i][2], en)]
    return out, errs


def merge(out):
    ns = names.load()
    for e in ns:
        e["en"] = out.get(e["id"], e["en"])
    names.PATH.write_text(json.dumps(ns, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    by_name = {e["id"]: e["en"] for e in ns}
    lab = load_labels()
    for e in lab:
        if e["name"]:
            e["en"] = by_name.get(e["name"], "")
        elif e["jp"]:
            e["en"] = out.get(f"L{e['idx']:03d}", e["en"])
    LABELS.write_text(json.dumps(lab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main():
    cmd = sys.argv[1]
    path = Path(sys.argv[2]) if len(sys.argv) > 2 else TL / "names.out.tsv"
    if cmd == "split":
        TL.mkdir(parents=True, exist_ok=True)
        (TL / "names.tsv").write_text("\n".join("\t".join(r) for r in rows()) + "\n", encoding="utf-8",
                                      newline="\n")
        print(len(rows()), "rows -> work/tl/names.tsv")
    elif cmd in ("check", "merge"):
        out, errs = check(path)
        for x in errs[:80]:
            print(x)
        if errs:
            sys.exit(f"{len(errs)} errors")
        if cmd == "merge":
            merge(out)
            print(f"merged {len(out)}")
        else:
            print("OK")


if __name__ == "__main__":
    main()
