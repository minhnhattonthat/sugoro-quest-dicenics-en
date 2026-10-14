"""Build the patched ROM.
    python -X utf8 tools/build.py [--marker] [--qa ID=TEXT].. [--out build/sq_en.sfc]
    python -X utf8 tools/build.py --identity       # JP repacked in place; must equal the original
English build: font (tools/font.py) -> asar asm/main.asm (VWF) -> main script groups relocated to free banks.
--marker: every string becomes "[id]" + filler on each text run (control codes kept), for the marker tour.
--qa ID=TEXT: override one string (en.tbl syntax) for width tests.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / ".claude/skills/translate-retro-game/scripts")]
from tbl import Table  # noqa: E402
import font  # noqa: E402
import gfxtext  # noqa: E402
import labels  # noqa: E402
import names  # noqa: E402
import plates  # noqa: E402
import text  # noqa: E402

ORIG = ROOT / "rom/orig.sfc"
ASAR = ROOT / "tools/asar/asar.exe"
EN = Table.load(ROOT / "tbl/en.tbl")
# Free space (all 0xFF in the original): (bank, first addr, end addr exclusive). $3A:8000-$AFFF holds asm/main.asm.
FREE = [(0x21, 0x8000, 0x10000), (0x26, 0x8000, 0x10000), (0x39, 0x8800, 0x10000), (0x3A, 0xB000, 0x10000)]
CTRL = re.compile(r"(\{[^}]*\})")
FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs."


def marker(e):
    """Keep JP control codes; replace each text run with [id] + filler (one run per line)."""
    out, first = [], True
    for part in CTRL.split(e["jp"]):
        if not part or CTRL.fullmatch(part):
            out.append(part)
            continue
        n = len(part)  # JP cells: fill about as many px as the JP line used (12 px each)
        s = (f"[{e['id']}] " if first else "") + FILLER
        out.append(s[:max(n * 2, len(e["id"]) + 3)])
        first = False
    return "".join(out)


def check_free(rom):
    for bank, lo, hi in FREE:
        a, b = text.script.lorom(bank, lo), text.script.lorom(bank, hi - 1) + 1
        if set(rom[a:b]) != {0xFF}:
            raise SystemExit(f"free range {bank:02X}:{lo:04X}-{hi:04X} is not empty in the original")


def place_groups(rom, groups, pick):
    """First-fit each group (table + strings) into FREE; returns {group: (bank, addr, size)}."""
    cursor = [lo for _, lo, _ in FREE]
    placed = {}
    for g, entries in groups.items():
        rels, blob = text.encode_group(entries, pick)
        size = 2 * len(entries) + len(blob)
        for i, (bank, lo, hi) in enumerate(FREE):
            if cursor[i] + size <= hi:
                text.write_group(rom, g, entries, pick, bank, cursor[i])
                placed[g] = (bank, cursor[i], size)
                cursor[i] += size
                break
        else:
            raise SystemExit(f"group {g} ({size} bytes) does not fit in free space")
    return placed


def asar(rom_path):
    font_bin, wid = font.pack()
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/en_font.bin").write_bytes(font_bin)
    (ROOT / "build/en_widths.bin").write_bytes(wid)
    r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ROOT / "asm/main.asm"), str(rom_path)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("asar failed:\n" + r.stdout + r.stderr)


def build(identity=False, marker_build=False, qa=None, out=None):
    rom = bytearray(ORIG.read_bytes())
    groups = text.load_groups()
    if identity:
        for g, entries in groups.items():
            text.write_group(rom, g, entries, lambda e: text.JP.encode(e["jp"]))
        return bytes(rom)
    check_free(rom)
    out = Path(out or ROOT / "build/sq_en.sfc")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(rom)
    asar(out)
    rom = bytearray(out.read_bytes())
    qa = qa or {}

    def pick(e):
        if e["id"] in qa:
            return EN.encode(qa[e["id"]])
        if marker_build:
            return EN.encode(marker(e))
        return EN.encode(e["en"]) if e["en"] else text.JP.encode(e["jp"])

    place_groups(rom, groups, pick)
    names.pack(rom, names.load(), lambda e: EN.encode(e["en"]) if e["en"] else names.JP.encode(e["jp"]))
    labels.pack(rom)
    gfxtext.pack(rom, ORIG.read_bytes())
    plates.pack(rom)
    out.write_bytes(rom)
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--qa", action="append", default=[])
    ap.add_argument("--out", default=str(ROOT / "build/sq_en.sfc"))
    a = ap.parse_args()
    qa = dict(s.split("=", 1) for s in a.qa)
    data = build(a.identity, a.marker, qa, a.out)
    if a.identity:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_bytes(data)
        print(a.out, "identical to original" if data == ORIG.read_bytes() else "DIFFERS from original")
    else:
        print(a.out)


if __name__ == "__main__":
    main()
