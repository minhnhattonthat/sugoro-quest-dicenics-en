"""Status-panel name plates: raw 4bpp at 0x6B000 + c*0x280 (c = character 0..5), 80x16 px as 10 top-row tiles then
10 bottom-row tiles; copied into the panel by $06:F429. Colours: fill 8, text F, outline B, bottom row B.
English: class in the condensed font (1-2 lines, left), name in the dialogue VWF (right).
    python -X utf8 tools/plates.py preview   -> work/plates.png
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill  # noqa: E402,F401  (puts the skill's scripts/ on sys.path)
import font  # noqa: E402
import labels  # noqa: E402

BASE, W, H = 0x6B000, 80, 16
FILL, INK, EDGE = 0x8, 0xF, 0xB
SPEC = ROOT / "script/plates.json"


def render(cls_lines, name):
    from tbl import Table
    en = Table.load(ROOT / "tbl/en.tbl")
    ink = [[0] * W for _ in range(H)]
    # class: condensed font, lines at y 0 / 8 (one line: y 4)
    ys = [4] if len(cls_lines) == 1 else [0, 7]
    for text, y0 in zip(cls_lines, ys):
        w = labels.text_width(text)
        bits = labels.render(text)
        shift = (64 - w) // 2
        for yy in range(7):
            row = 0
            for t in range(8):
                row = (row << 8) | bits[t * 8 + yy]
            row = (row << shift) & ((1 << 64) - 1)
            for c in range(64):
                if row & (1 << (63 - c)) and 1 + c < W and y0 + yy < H - 1:
                    ink[y0 + yy][1 + c] = 1
    # name: VWF glyph ink rows 2..14, right-aligned
    codes = en.encode(name)
    wid = sum(font.widths().get(k, 0) for k in codes)
    x = W - 2 - wid
    g = font.pack()[0]
    for k in codes:
        for yy in range(16):
            b = g[32 * k + 2 * yy + 1]
            for bit in range(8):
                if b & (0x80 >> bit) and 0 <= yy - 1 < H - 1:
                    ink[yy - 1][x + bit] = 1
        x += font.widths().get(k, 0)
    px = [[FILL] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if ink[y][x]:
                px[y][x] = INK
            elif any(0 <= y + dy < H and 0 <= x + dx < W and ink[y + dy][x + dx]
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                px[y][x] = EDGE
    px[H - 1] = [EDGE] * W
    return px


def to_tiles(px):
    out = bytearray(0x280)
    for row in range(2):
        for t in range(10):
            tile = bytearray(32)
            for y in range(8):
                for x in range(8):
                    v = px[row * 8 + y][t * 8 + x]
                    for p in range(4):
                        if v & (1 << p):
                            tile[(p // 2) * 16 + 2 * y + (p & 1)] |= 0x80 >> x
            out[(row * 10 + t) * 32:(row * 10 + t + 1) * 32] = tile
    return bytes(out)


def pack(rom):
    for c, e in enumerate(json.loads(SPEC.read_text(encoding="utf-8"))):
        rom[BASE + c * 0x280:BASE + (c + 1) * 0x280] = to_tiles(render(e["class"], e["name"]))


def preview():
    from PIL import Image
    pal = {FILL: (200, 200, 230), INK: (255, 255, 255), EDGE: (60, 60, 140)}
    img = Image.new("RGB", (W, H * 6 + 10), (0, 0, 0))
    for c, e in enumerate(json.loads(SPEC.read_text(encoding="utf-8"))):
        for y, row in enumerate(render(e["class"], e["name"])):
            for x, v in enumerate(row):
                img.putpixel((x, c * (H + 2) + y), pal.get(v, (255, 0, 0)))
    img.resize((W * 5, img.height * 5), Image.NEAREST).save(ROOT / "work/plates.png")
    print(ROOT / "work/plates.png")


if __name__ == "__main__":
    preview()
