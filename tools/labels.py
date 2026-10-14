"""Pre-rendered 1bpp name labels at 0x90000: 64x8 px each (8 tiles x 8 bytes, bit 7 = left).
    python -X utf8 tools/labels.py sheet [FIRST COUNT]   -> work/labels_FIRST.png, indexed, zoom 3
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
BASE, N = 0x90000, 240


def label_px(rom, i):
    """-> 8 rows of 64 bools"""
    b = rom[BASE + 64 * i: BASE + 64 * i + 64]
    return [[bool(b[t * 8 + y] & (0x80 >> x)) for t in range(8) for x in range(8)] for y in range(8)]


COND = ROOT / "font" / "cond8.txt"
WIDTH = 64


def cond_glyphs():
    """{char: [8 row strings]} from font/cond8.txt (3 columns, 8 rows)."""
    glyphs, cur = {}, None
    for line in COND.read_text(encoding="utf-8").splitlines():
        if line.startswith("char "):
            cur = " " if line[5:] == "space" else line[5:]
            glyphs[cur] = []
        elif cur is not None and line and set(line) <= {".", "#"}:
            glyphs[cur].append(line)
    return glyphs


GLYPHS = cond_glyphs()


def text_width(text):
    """Proportional: advance = ink width + 1 (space 2), minus the trailing gap."""
    w = 0
    for ch in text:
        rows = GLYPHS[ch]
        cols = [x for x in range(3) if any(r[x] == "#" for r in rows)]
        w += (cols[-1] + 1 if cols else 2) + 1
    return max(w - 1, 0)


def render(text):
    """-> 64 bytes (8 tiles x 8 rows, bit 7 = left), text centred. Raises if wider than 64 px."""
    w = text_width(text)
    if w > WIDTH:
        raise ValueError(f"label {text!r} is {w}px > {WIDTH}")
    px = [[0] * WIDTH for _ in range(8)]
    x = (WIDTH - w) // 2
    for ch in text:
        rows = GLYPHS[ch]
        cols = [c for c in range(3) if any(r[c] == "#" for r in rows)]
        gw = cols[-1] + 1 if cols else 2
        for y, r in enumerate(rows):
            for c in range(gw):
                if r[c] == "#":
                    px[y][x + c] = 1
        x += gw + 1
    out = bytearray(64)
    for t in range(8):
        for y in range(8):
            out[t * 8 + y] = sum(0x80 >> c for c in range(8) if px[y][t * 8 + c])
    return bytes(out)


def sheet(rom, first, count, zoom=3):
    cols = 4
    rows = (count + cols - 1) // cols
    img = Image.new("RGB", (cols * 100, rows * 14), "white")
    d = ImageDraw.Draw(img)
    for k in range(count):
        i = first + k
        x0, y0 = (k % cols) * 100, (k // cols) * 14
        d.text((x0, y0 + 2), f"{i:3d}", fill=(0, 0, 255))
        for y, row in enumerate(label_px(rom, i)):
            for x, on in enumerate(row):
                if on:
                    img.putpixel((x0 + 24 + x, y0 + 3 + y), (0, 0, 0))
    out = ROOT / f"work/labels_{first:03d}.png"
    img.resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    if sys.argv[1] == "sheet":
        first = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        sheet(rom, first, int(sys.argv[3]) if len(sys.argv) > 3 else 60)
