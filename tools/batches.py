"""Translation batches: split -> agents translate -> check -> merge; pairs files for reviewers.

    python -X utf8 tools/batches.py list                # batch names and sizes
    python -X utf8 tools/batches.py split b7a           # work/tl/b7a.tsv + work/tl/terms_b7a.txt
    python -X utf8 tools/batches.py check b7a           # validates work/tl/b7a.out.tsv, prints OK or errors
    python -X utf8 tools/batches.py merge b7a           # check, then write "en" into script/g*.json
    python -X utf8 tools/batches.py pairs b7a           # work/tl/b7a.pairs.txt for the reviewer
    python -X utf8 tools/batches.py apply FILE          # id<TAB>EN fixes (any batch), checked, merged
    python -X utf8 tools/batches.py fit "TEXT"          # px per line, for trying a line before writing it

TSV in: id<TAB>limit<TAB>hint<TAB>jp (raw, control codes included). limit = "lines per page / px per line".
TSV out: id<TAB>English with the same control codes; {nl} = line break (the game does not wrap).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import lint  # noqa: E402
import text  # noqa: E402

TL = ROOT / "work" / "tl"
TOKEN = re.compile(r"\{[^}]*\}")


def all_entries():
    """[(group, entry)] in script order, unique strings only."""
    return [(g, e) for g, es in text.load_groups().items() for e in es if "same" not in e]


def ids_of(groups, part=None, parts=1):
    es = [e["id"] for g, e in all_entries() if g in groups]
    if part is None:
        return es
    n = (len(es) + parts - 1) // parts
    return es[part * n:(part + 1) * n]


BATCHES = {
    "b1": lambda: ids_of({0, 1}), "b2": lambda: ids_of({2}), "b3": lambda: ids_of({3}),
    "b4": lambda: ids_of({4}), "b5a": lambda: ids_of({5}, 0, 2), "b5b": lambda: ids_of({5}, 1, 2),
    "b6a": lambda: ids_of({6}, 0, 2), "b6b": lambda: ids_of({6}, 1, 2),
"b7a": lambda: ids_of({7}, 0, 2), "b7b": lambda: ids_of({7}, 1, 2),
}


def by_id():
    return {e["id"]: e for _, e in all_entries()}


def glossary():
    """Rows of every glossary table: (jp, [en alternatives], [avoid])."""
    rows = []
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) < 2 or cells[0] in ("JP", "") or set(cells[0]) <= {"-"}:
            continue
        avoid = [a.strip() for a in cells[4].split(",") if a.strip()] if len(cells) > 4 else []
        rows.append((cells[0], [a.strip() for a in cells[1].split("/") if a.strip()], avoid))
    return rows


def limit(e):
    pages = e["jp"].split("{clr}")
    lines = "+".join(str(len(p.split("{nl}"))) for p in pages if p.strip() or len(pages) == 1)
    wide = any(lint.jp_cells(x) > 18 for p in pages for x in p.split("{nl}"))
    return f"{lines}L/{lint.WIDE_PX if wide else lint.LINE_PX}px"


def hint(e):
    """Choice rows ("    はい     いいえ"): the cell where each option starts, as {atN} to copy."""
    out = []
    for line in e["jp"].split("{nl}"):
        plain = TOKEN.sub("", line)
        if re.fullmatch(r" +\S+( {2,}\S+)+ *", plain):
            cells = [m.start() for m in re.finditer(r"\S+", plain)]
            out.append("choice:" + "".join(f"{{at{c}}}{w}" for c, w in zip(cells, plain.split())))
    return " ".join(out) or "-"


KATA = re.compile(r"[ァ-ヶー]")


def term_in(term, jp, gloss):
    """term occurs in jp as a word: not inside a longer glossary term, and a katakana term is not part of a
    longer katakana word (マス in フェイマス)."""
    longer = sorted({t for t, _, _ in gloss if term in t and t != term}, key=len, reverse=True)
    for t in longer:
        jp = jp.replace(t, "\0" * len(t))
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if KATA.match(term[0]) and a > 0 and KATA.match(jp[a - 1]):
            continue
        if KATA.match(term[-1]) and b < len(jp) and KATA.match(jp[b]):
            continue
        return True
    return False


def problems(e, en, gloss):
    errs = lint.lint_entry({"id": e["id"], "jp": e["jp"], "en": en})
    if "\t" in en or "\\" in en:
        errs.append("tab or backslash in text")
    jp_text = e["jp"]
    for jp, alts, avoid in gloss:
        if term_in(jp, jp_text, gloss) and alts and not any(a.lower() in en.lower() for a in alts):
            errs.append(f"glossary: {jp} -> {' / '.join(alts)} missing")
        for a in avoid:
            if re.search(rf"\b{re.escape(a)}\b", en):
                errs.append(f"glossary: avoid {a!r}")
    if TOKEN.sub("", e["jp"]).strip() and not TOKEN.sub("", en).strip():
        errs.append("empty translation")
    return errs


def read_out(path):
    out = {}
    for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        if "\t" not in line:
            raise SystemExit(f"{path.name}:{n}: no tab")
        i, en = line.split("\t", 1)
        if i in out:
            raise SystemExit(f"{path.name}:{n}: duplicate id {i}")
        out[i] = en.rstrip("\r\n")
    return out


def check(name, path=None, require_all=True):
    ents = by_id()
    if name:
        tsv = (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines()
        es = {ln.split("\t")[0]: ents[ln.split("\t")[0]] for ln in tsv if ln.strip()}
    else:
        es = ents
    out = read_out(path or TL / f"{name}.out.tsv")
    errs = []
    if require_all:
        errs += [f"{i}: missing" for i in es if i not in out]
    errs += [f"{i}: unknown id" for i in out if i not in es]
    gloss = glossary()
    for i, en in out.items():
        if i in es:
            errs += [f"{i}: {p}" for p in problems(es[i], en, gloss)]
    return out, errs


def merge(out):
    for g, es in text.load_groups().items():
        for e in es:
            if e["id"] in out:
                e["en"] = out[e["id"]]
        text.save(text.SCRIPT / f"g{g}.json", es)


def split(name):
    TL.mkdir(parents=True, exist_ok=True)
    ents = by_id()
    es = [ents[i] for i in BATCHES[name]() if not ents[i]["en"]]
    lines = [f"{e['id']}\t{limit(e)}\t{hint(e)}\t{e['jp']}" for e in es]
    (TL / f"{name}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    alltext = " ".join(e["jp"] for e in es)
    terms = [ln for ln in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines()
             if ln.startswith("|") and (cell := ln.strip("|").split("|")[0].strip()) and cell in alltext]
    (TL / f"terms_{name}.txt").write_text("\n".join(terms) + "\n", encoding="utf-8", newline="\n")
    print(f"{name}: {len(es)} entries, {len(terms)} terms -> work/tl/{name}.tsv")


def pairs(name):
    ids = set(BATCHES[name]())
    order = [e for _, e in all_entries()]
    out = []
    for k, e in enumerate(order):
        if e["id"] not in ids:
            continue
        for c in order[max(0, k - 2):k]:
            out.append(f"   {c['id']} | {c['jp']}\n   {c['en']}")
        out.append(f">> {e['id']} | {e['jp']}\n>> {e['en']}")
        for c in order[k + 1:k + 3]:
            out.append(f"   {c['id']} | {c['jp']}\n   {c['en']}")
        out.append("")
    (TL / f"{name}.pairs.txt").write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"work/tl/{name}.pairs.txt")


def report(errs):
    for x in errs[:60]:
        print(x)
    if len(errs) > 60:
        print(f"... {len(errs) - 60} more")


def main():
    cmd, arg = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
    if cmd == "list":
        ents = by_id()
        for b, f in BATCHES.items():
            es = [ents[i] for i in f()]
            done = sum(1 for e in es if e["en"])
            print(f"{b}: {len(es)} entries, {sum(len(TOKEN.sub('', e['jp'])) for e in es)} jp chars, {done} done")
    elif cmd == "split":
        split(arg)
    elif cmd == "pairs":
        pairs(arg)
    elif cmd == "fit":
        for line in arg.split("{nl}"):
            print(f"{lint.line_px(line):4d}px  {line}")
    elif cmd in ("check", "merge", "apply"):
        out, errs = check(None, Path(arg), require_all=False) if cmd == "apply" else check(arg)
        report(errs)
        if errs:
            sys.exit(f"{len(errs)} errors")
        if cmd != "check":
            merge(out)
            print(f"merged {len(out)}")
        else:
            print("OK")


if __name__ == "__main__":
    main()
