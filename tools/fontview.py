"""Render the 16x16 2bpp main font (bank $11, 64 bytes/glyph: TL TR BL BR tiles) as a labelled sheet.
    python -X utf8 tools/fontview.py [ROM] [OUT.png] [--first 0 --count 512]
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
FONT_OFF = 0x88000


def tile2bpp(b):
    return [[((b[2 * y] >> (7 - x)) & 1) | (((b[2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]


def glyph(rom, code, off=FONT_OFF):
    g = rom[off + code * 64: off + code * 64 + 64]
    px = [[0] * 16 for _ in range(16)]
    for t, (tx, ty) in enumerate([(0, 0), (8, 0), (0, 8), (8, 8)]):
        for y, row in enumerate(tile2bpp(g[t * 16:t * 16 + 16])):
            for x, v in enumerate(row):
                px[ty + y][tx + x] = v
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "rom/orig.sfc"))
    ap.add_argument("out", nargs="?", default=str(ROOT / "work/font.png"))
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=512)
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    cols, cw, ch = 16, 20, 30
    rows = (a.count + cols - 1) // cols
    img = Image.new("RGB", (cols * cw + 30, rows * ch), "white")
    d = ImageDraw.Draw(img)
    pal = [(255, 255, 255), (0, 0, 0), (200, 80, 80), (80, 80, 200)]
    for i in range(a.count):
        code = a.first + i
        r, c = divmod(i, cols)
        if c == 0:
            d.text((0, r * ch + 4), f"{code:03X}", fill=(0, 0, 255))
        for y, row in enumerate(glyph(rom, code)):
            for x, v in enumerate(row):
                if v:
                    img.putpixel((30 + c * cw + x, r * ch + y), pal[v])
    img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
