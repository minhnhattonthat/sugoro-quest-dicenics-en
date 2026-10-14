"""View a 4bpp block as a 128-px-wide bitmap (16 tiles per row), with a 4 px ruler grid, zoom 4.
    python -X utf8 tools/winview.py BLOCK [--before]   -> work/win_<block>.png  (built block unless --before)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import strips  # noqa: E402

PAL = [(0, 0, 0), (40, 40, 40), (90, 90, 90), (255, 255, 255)] + [(60 + 12 * i, 80 + 10 * i, 160 + 6 * i) for i in range(12)]


def bitmap(data):
    rows = len(data) // 32 // 16
    img = Image.new("RGB", (128, rows * 8))
    for r in range(rows):
        for t in range(16):
            for y in range(8):
                for x in range(8):
                    img.putpixel((t * 8 + x, r * 8 + y), PAL[strips.px4(data, r * 16 + t, x, y)])
    return img


def main():
    bid = sys.argv[1]
    data = strips.block(bid)
    if "--before" not in sys.argv:
        import gfxtext
        data = gfxtext.apply((ROOT / "rom/orig.sfc").read_bytes()).get(bid, data)
    img = bitmap(data).resize((128 * 4, len(data) // 32 // 16 * 32), Image.NEAREST)
    d = ImageDraw.Draw(img)
    for y in range(0, img.height, 16):
        d.line([(0, y), (4, y)], fill=(255, 0, 0))
    out = ROOT / f"work/win_{bid}.png"
    img.save(out)
    print(out)


if __name__ == "__main__":
    main()
