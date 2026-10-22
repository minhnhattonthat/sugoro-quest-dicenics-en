"""Decode a ROM range with jp.tbl, one line per E0/FD-terminated chunk.  python -X utf8 tools/peek.py START END"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import skill  # noqa: E402,F401  (puts the skill's scripts/ on sys.path)
from tbl import Table  # noqa: E402

rom = (ROOT / "rom/orig.sfc").read_bytes()
t = Table.load(ROOT / "tbl/jp.tbl")
a, b = (int(x, 16) for x in sys.argv[1:3])
o = a
while o < b:
    e = o
    while e < b and rom[e] not in (0xE0, 0xFD):
        e += 2 if rom[e] in (0xFE, 0xFF) else 1
    print(f"{o:06X} {t.decode(rom, o, min(e, b) - o)[0]}")
    o = e + 1
