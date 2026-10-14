"""Concatenate 4bpp blocks (16 tiles wide) into one tall bitmap and draw a grid (labels every 8 px).
    python -X utf8 tools/tallview.py OUT.png BLOCK.. [--built]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import strips  # noqa: E402
import winview  # noqa: E402

out, bids = sys.argv[1], [b for b in sys.argv[2:] if not b.startswith("--")]
datas = [strips.block(b) for b in bids]
if "--built" in sys.argv:
    import gfxtext
    new = gfxtext.apply((ROOT / "rom/orig.sfc").read_bytes())
    datas = [new.get(b, d) for b, d in zip(bids, datas)]
imgs = [winview.bitmap(d) for d in datas]
H = sum(i.height for i in imgs)
Z = 3
canvas = Image.new("RGB", (128 * Z + 40, H * Z), (30, 0, 30))
y = 0
for i in imgs:
    canvas.paste(i.resize((128 * Z, i.height * Z), Image.NEAREST), (40, y * Z))
    y += i.height
d = ImageDraw.Draw(canvas)
for yy in range(0, H, 8):
    d.text((2, yy * Z), str(yy), fill=(255, 255, 0))
    d.line([(36, yy * Z), (40, yy * Z)], fill=(255, 255, 0))
for xx in range(0, 128, 16):
    d.line([(40 + xx * Z, 0), (40 + xx * Z, 3)], fill=(255, 255, 0))
canvas.save(out)
print(out, H)
