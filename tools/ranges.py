"""Write tools/allowed_ranges.txt: every file range the English build may change (romdiff gate in tests/test_build.py).
    python -X utf8 tools/ranges.py
Regenerate after adding a new kind of write; the test then fails on anything outside these.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill  # noqa: E402,F401  (puts the skill's scripts/ on sys.path)
import build  # noqa: E402
import gfx_assets  # noqa: E402
import gfxtext  # noqa: E402
import labels  # noqa: E402
import names  # noqa: E402
import font8  # noqa: E402
import panelart  # noqa: E402
import rankart  # noqa: E402
import namekb  # noqa: E402
import plates  # noqa: E402
import script  # noqa: E402


def ranges():
    out = [(0x40121, 0x40124, "VWF hook JSL"), (script.GROUP_TABLE, script.GROUP_TABLE + 3 * 8 - 1, "group table")]
    for bank, lo, hi in build.FREE:
        out.append((script.lorom(bank, lo), script.lorom(bank, hi - 1), f"free bank {bank:02X}: script / asm"))
    out.append((0x1D0000, 0x1D2FFF, "asm/main.asm + font (bank 3A)"))
    for bank, r in names.REGIONS.items():
        for a, b in r["text"] + r["free"]:
            out.append((a, b - 1, f"names bank {bank:02X}"))
    for bank, first, n, stride in names.SLOTS:
        out.append((first, first + (n - 1) * stride + 1, f"name slots bank {bank:02X}"))
    out.append((labels.BASE, labels.BASE + 64 * labels.N - 1, "1bpp labels"))
    for a, b in gfxtext.GFX_FREE:
        out.append((a, b - 1, "recompressed gfx"))
    refs = {src: r for src, (_, _, r) in gfx_assets.assets().items()}
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    for bid in gfxtext.apply(rom):
        for r in refs[int(bid, 16)]:
            out.append((r + 1, r + 3, f"loader -> {bid}"))
    out.append((plates.BASE, plates.BASE + 6 * 0x280 - 1, "status plates"))
    out.append((*font8.RANGE, "8x8 panel font: a-z, apostrophe"))
    out += [(a, b, "panel art: Diceman lines") for a, b in panelart.RANGES]
    out += [(a, b, "rank screen names") for a, b in rankart.RANGES]
    out += [(a, b, "name entry key tables, JP-font a-z") for a, b in namekb.RANGES]
    out += [(0x3AF80, 0x3AF84, "panel string rowstart hook"), (0x3AFCF, 0x3AFDD, "panel string draw hook")]
    out.append((build.RANKING, build.RANKING + 39, "default ranking names"))
    return out


def main():
    lines = [f"{a:06X}-{b:06X}  # {why}" for a, b, why in ranges()]
    (ROOT / "tools/allowed_ranges.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(len(lines), "ranges")


if __name__ == "__main__":
    main()
