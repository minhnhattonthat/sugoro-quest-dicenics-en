"""Rule-setup windows (sprites). Six LZ blocks form one 128x192 4bpp sheet (16 tiles wide, 4 tile rows each).
A window (80x64 on screen) is built from three tile-row pairs R0..R2 (cols 0-9) plus a 4th sprite row made of
R0 cols 10-15 (48 px) and R1 cols 10-13 (32 px) - read from OAM on the rule screen (sprites 0x120.. at VRAM A400).
Window k starts at sheet y = 48*k.  Text: colour 3, lines 9 px apart starting at window y 2.
    python -X utf8 tools/rulewin.py ascii K      # print window K
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import lz  # noqa: E402

BLOCKS = ["11AFE7", "11B489", "11B8C5", "11BCBA", "11BEF9", "11C2C8"]
TEXT = 3


class Sheet:
    def __init__(self, datas):
        self.datas = datas  # list of bytearrays, 64 tiles each (16 x 4)

    def _loc(self, x, y):
        b, yy = divmod(y, 32)
        r, py = divmod(yy, 8)
        t = r * 16 + x // 8
        return self.datas[b], t, x % 8, py

    def get(self, x, y):
        d, t, px, py = self._loc(x, y)
        return sum(((d[t * 32 + (p // 2) * 16 + 2 * py + (p & 1)] >> (7 - px)) & 1) << p for p in range(4))

    def set(self, x, y, v):
        d, t, px, py = self._loc(x, y)
        for p in range(4):
            i = t * 32 + (p // 2) * 16 + 2 * py + (p & 1)
            if v & (1 << p):
                d[i] |= 0x80 >> px
            else:
                d[i] &= ~(0x80 >> px) & 0xFF


def window_map(k):
    """window pixel (wx, wy) -> sheet pixel (x, y), for wx < 80, wy < 64"""
    base = 48 * k

    def f(wx, wy):
        row = wy // 16
        if row < 3:
            return wx, base + 16 * row + wy % 16
        if wx < 48:
            return 80 + wx, base + wy % 16
        return 80 + (wx - 48), base + 16 + wy % 16
    return f


def load(rom):
    return Sheet([bytearray(lz.decompress(rom, int(b, 16))[0]) for b in BLOCKS])


def ascii_window(sheet, k):
    f = window_map(k)
    for wy in range(64):
        print(f"{wy:2d} " + "".join("0123456789ABCDEF"[sheet.get(*f(wx, wy))] for wx in range(80)))


def rewrite(sheet, k, lines, x0=9, y0=2, pitch=9):
    """Erase all text in window k's interior (each pixel row -> its gradient colour) and draw lines[i] at
    window y = y0 + pitch*i in the condensed font, colour 3."""
    import labels
    f = window_map(k)
    for wy in range(2, 62):
        bg = Counter(sheet.get(*f(wx, wy)) for wx in range(2, 78)).most_common()
        bgc = next(c for c, _ in bg if c != TEXT)
        for wx in range(2, 78):
            if sheet.get(*f(wx, wy)) == TEXT:
                sheet.set(*f(wx, wy), bgc)
    for i, text in enumerate(lines):
        top = y0 + pitch * i
        w = labels.text_width(text)
        if x0 + w > 76:
            raise ValueError(f"{text!r}: {w}px too wide for the window")
        bits = labels.render(text)
        shift = (64 - w) // 2
        for y in range(8):
            row = 0
            for t in range(8):
                row = (row << 8) | bits[t * 8 + y]
            row = (row << shift) & ((1 << 64) - 1)
            for c in range(64):
                if row & (1 << (63 - c)) and top + y < 62:
                    sheet.set(*f(x0 + c, top + y), TEXT)


def apply(rom, spec):
    """spec: {"windows": [{"k", "pitch", "lines": [...]}]} -> {block id: bytes}"""
    sheet = load(rom)
    for w in spec["windows"]:
        rewrite(sheet, w["k"], w["lines"], y0=w.get("y0", 2), pitch=w["pitch"])
    return dict(zip(BLOCKS, sheet.datas))


if __name__ == "__main__":
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    if sys.argv[1] == "ascii":
        ascii_window(load(rom), int(sys.argv[2]))
