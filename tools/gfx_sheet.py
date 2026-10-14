"""Render decompressed blocks in work/gfx/*.bin as 2bpp tiles (grey ramp), several blocks per survey sheet.
    python -X utf8 tools/gfx_sheet.py [--fmt snes2|snes4] [--per 6] [--cols 32]  -> work/gfx/sheet_NN.png
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent


def tiles(data, bpp, cols):
    size = 8 * bpp
    n = len(data) // size
    rows = (n + cols - 1) // cols
    img = Image.new("L", (cols * 8, max(rows, 1) * 8), 0)
    px = img.load()
    for t in range(n):
        b = data[t * size:(t + 1) * size]
        ox, oy = (t % cols) * 8, (t // cols) * 8
        for y in range(8):
            for x in range(8):
                v = 0
                for p in range(bpp):
                    byte = b[(p // 2) * 16 + 2 * y + (p & 1)]
                    v |= ((byte >> (7 - x)) & 1) << p
                px[ox + x, oy + y] = v * (255 // ((1 << bpp) - 1))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmt", default="snes2")
    ap.add_argument("--per", type=int, default=6)
    ap.add_argument("--cols", type=int, default=32)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    bpp = {"snes2": 2, "snes4": 4}[a.fmt]
    files = sorted((ROOT / "work/gfx").glob("*.bin"))
    if a.only:
        files = [f for f in files if f.stem in a.only]
    for s in range(0, len(files), a.per):
        imgs = [(f.stem, tiles(f.read_bytes(), bpp, a.cols)) for f in files[s:s + a.per]]
        h = sum(i.height + 12 for _, i in imgs)
        sheet = Image.new("RGB", (a.cols * 8, h), (60, 0, 60))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, i in imgs:
            d.text((2, y), name, fill=(255, 255, 0))
            sheet.paste(i.convert("RGB"), (0, y + 12))
            y += i.height + 12
        out = ROOT / f"work/gfx/{a.fmt}_{s // a.per:02d}.png"
        sheet.resize((sheet.width * a.zoom, sheet.height * a.zoom), Image.NEAREST).save(out)
        print(out.name, [n for n, _ in imgs])


if __name__ == "__main__":
    main()
