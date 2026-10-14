"""Lint English script entries.
    python -X utf8 tools/lint.py [FILES..]     (default: script/g*.json); exit 1 on errors
Rules per string with "en":
  - encodable with tbl/en.tbl, no Japanese left, no banned chars (; * < > @ hold other glyphs in the art)
  - control codes other than {nl} and {atN} in the same order as JP
  - per page ({clr}-separated): EN lines <= JP lines; per line: px <= 216 (240 if the JP line used > 18 cells)
  - {v1}..{v15} counted at VAR_PX (names / numbers inserted at run time)
  - no ordinal suffix glued to a variable ({v1}st)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / ".claude/skills/translate-retro-game/scripts")]
from tbl import Table  # noqa: E402
import font  # noqa: E402

EN = Table.load(ROOT / "tbl/en.tbl")
WID = font.widths()
# px budget for run-time inserts: v9 = number, v1-v4/v7 = actor (character/monster) names, others = item/spell names
VAR_PX = {9: 30, 1: 60, 2: 60, 3: 60, 4: 60, 7: 60}
VAR_PX_ITEM = 100
BATTLE_ACTOR_PX = 82  # group 1 (battle) messages: {v1}..{v7} may be a monster ("Bird of Paradise")
LINE_PX, WIDE_PX = 216, 240
TOKEN = re.compile(r"(\{[^}]*\})")
JP_RE = re.compile(r"[぀-ヿ一-鿿＀-￯]")
BANNED = set(";*<>@")


def char_px(ch):
    code = EN.encode(ch)
    return WID.get(code[0], 0) if len(code) == 1 else 0


def line_px(line, battle=False):
    px = 0
    for part in TOKEN.split(line):
        if not part:
            continue
        if part.startswith("{"):
            m = re.fullmatch(r"\{at(\d+)\}", part)
            if m:
                px = max(px, int(m[1]) * 12)
            elif re.fullmatch(r"\{v\d+\}", part):
                n = int(part[2:-1])
                w = VAR_PX.get(n, VAR_PX_ITEM)
                px += BATTLE_ACTOR_PX if battle and n != 9 and w < VAR_PX_ITEM else w
            continue
        px += sum(char_px(c) for c in part)
    return px


def jp_cells(line):
    return len(TOKEN.sub("", line)) + 4 * len(re.findall(r"\{v\d+\}", line))


def controls(s):
    """Ordered control codes that must match JP. {vN} inserts are checked as a set (EN may repeat a name)."""
    return [t for t in TOKEN.findall(s) if t != "{nl}" and not t.startswith("{at") and not re.fullmatch(r"\{v\d+\}", t)]


def var_set(s):
    return set(re.findall(r"\{v\d+\}", s))


def lint_entry(e):
    errs = []
    en, jp = e["en"], e["jp"]
    if JP_RE.search(en):
        errs.append("Japanese left in en")
    bad = BANNED & set(en)
    if bad:
        errs.append(f"banned chars {''.join(sorted(bad))}")
    try:
        EN.encode(en)
    except Exception as x:  # noqa: BLE001
        errs.append(f"not encodable: {x}")
        return errs
    if controls(en) != controls(jp):
        errs.append(f"control codes differ: JP {controls(jp)} EN {controls(en)}")
    if var_set(en) != var_set(jp):
        errs.append(f"variables differ: JP {sorted(var_set(jp))} EN {sorted(var_set(en))}")
    if re.search(r"\{v\d+\}(st|nd|rd|th)\b", en):
        errs.append("ordinal suffix glued to a variable")
    jp_pages, en_pages = jp.split("{clr}"), en.split("{clr}")
    for pi, (jpage, epage) in enumerate(zip(jp_pages, en_pages), 0 if jp.startswith("{clr}") else 1):
        jl, el = jpage.split("{nl}"), epage.split("{nl}")
        if len(el) > len(jl):
            errs.append(f"page {pi + 1}: {len(el)} lines > JP {len(jl)}")
        wide = any(jp_cells(x) > 18 for x in jl)
        lim = WIDE_PX if wide else LINE_PX
        for li, line in enumerate(el):
            px = line_px(line, battle=e["id"].startswith("1"))
            if px > lim:
                errs.append(f"page {pi + 1} line {li + 1}: {px}px > {lim}px: {TOKEN.sub('', line)[:40]!r}")
    return errs


def main():
    files = [Path(f) for f in sys.argv[1:]] or sorted((ROOT / "script").glob("g[0-9].json"))
    n_err = n_done = 0
    for f in files:
        for e in json.loads(f.read_text(encoding="utf-8")):
            if "same" in e or not e.get("en"):
                continue
            n_done += 1
            for err in lint_entry(e):
                print(f"{f.stem} {e['id']}: {err}")
                n_err += 1
    print(f"lint: {n_done} strings, {n_err} errors")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
