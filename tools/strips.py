"""Text strips in 4bpp OBJ blocks drawn over horizontal gradient bars (rule / option windows).
    python -X utf8 tools/strips.py segments BLOCK..     # print text segments: row, first tile, count
    python -X utf8 tools/strips.py sheet BLOCK..        # work/strips_<block>.png: segments numbered, zoom 4
Background of a pixel row = its most common colour across the 16 tiles; a tile belongs to text when any of its
pixels differs from that background.
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import lz  # noqa: E402

COLS = 16


def block(bid):
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    return bytearray(lz.decompress(rom, int(bid, 16))[0])


def px4(data, t, x, y):
    b = data[t * 32:t * 32 + 32]
    return sum(((b[(p // 2) * 16 + 2 * y + (p & 1)] >> (7 - x)) & 1) << p for p in range(4))


def row_bg(data, r):
    """background colour per pixel row (8) of tile row r"""
    return [Counter(px4(data, r * COLS + t, x, y) for t in range(COLS) for x in range(8)).most_common(1)[0][0]
            for y in range(8)]


def segments(data):
    """[(row, first tile col, count)]"""
    out = []
    for r in range(len(data) // 32 // COLS):
        bg = row_bg(data, r)
        text = [any(px4(data, r * COLS + t, x, y) != bg[y] for x in range(8) for y in range(8)) for t in range(COLS)]
        t = 0
        while t < COLS:
            if text[t]:
                a = t
                while t < COLS and text[t]:
                    t += 1
                out.append((r, a, t - a))
            t += 1
    return out


def sheet(bid):
    from PIL import Image, ImageDraw
    data = block(bid)
    segs = segments(data)
    rows = len(data) // 32 // COLS
    img = Image.new("RGB", (COLS * 8 + 40, rows * 12), (40, 0, 40))
    d = ImageDraw.Draw(img)
    pal = [(0, 0, 0)] + [((c * 53) % 256, (c * 97) % 256, (c * 151) % 256) for c in range(1, 16)]
    for r in range(rows):
        for t in range(COLS):
            for y in range(8):
                for x in range(8):
                    img.putpixel((40 + t * 8 + x, r * 12 + y), pal[px4(data, r * COLS + t, x, y)])
    for k, (r, a, n) in enumerate(segs):
        d.text((2, r * 12 - 2), f"{r}", fill=(255, 255, 0))
        d.rectangle([40 + a * 8, r * 12 + 8, 40 + (a + n) * 8 - 1, r * 12 + 9], fill=(0, 255, 0))
    out = ROOT / f"work/strips_{bid}.png"
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    cmd, bids = sys.argv[1], sys.argv[2:]
    for b in bids:
        if cmd == "segments":
            print(b, segments(block(b)))
        else:
            sheet(b)
