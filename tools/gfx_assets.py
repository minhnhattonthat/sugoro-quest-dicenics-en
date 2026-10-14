"""List LZSS-compressed assets referenced by load scripts (op 04: src24 dst24, see docs/re/graphics.md), decompress
them to work/gfx/<off>.bin and render previews.
    python -X utf8 tools/gfx_assets.py list|dump [--render]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from lz import decompress  # noqa: E402

rom = (ROOT / "rom/orig.sfc").read_bytes()
PAT = re.compile(rb"\x04(..)([\x80-\xbf\x00-\x3f])(..)([\x7e\x7f])", re.S)


def lorom(bank, addr):
    return ((bank & 0x7F) << 15) | (addr & 0x7FFF)


def assets():
    found = {}
    for m in PAT.finditer(rom):
        a = m[1][0] | m[1][1] << 8
        if a < 0x8000:
            continue
        src = lorom(m[2][0], a)
        size = rom[src] | rom[src + 1] << 8
        if not 0x20 <= size <= 0x10000:
            continue
        try:
            data, used = decompress(rom, src)
        except IndexError:
            continue
        if used < 8 or used > 2 * size + 8:
            continue
        found.setdefault(src, (len(data), used, []))[2].append(m.start())
    return found


def main():
    found = assets()
    if sys.argv[1:2] == ["list"]:
        for src, (n, used, refs) in sorted(found.items()):
            print(f"{src:06X} out {n:5X} in {used:5X} refs {' '.join(f'{r:06X}' for r in refs[:4])}")
        print(len(found), "assets")
    elif sys.argv[1:2] == ["dump"]:
        out = ROOT / "work/gfx"
        out.mkdir(parents=True, exist_ok=True)
        for src in sorted(found):
            (out / f"{src:06X}.bin").write_bytes(decompress(rom, src)[0])
        print(len(found), "->", out)


if __name__ == "__main__":
    main()
