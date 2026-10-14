"""Graphics text in LZSS blocks: redraw English into the tiles a screen's tilemap shows, recompress, relocate,
repoint every loader (op 04 entries found by tools/gfx_assets.py).
    python -X utf8 tools/gfxtext.py preview      # work/gfxtext/<block>.png before/after
Specs (script/gfxtext.json): {"blocks": {"<canvas base tile hex>": "<block id>"}, "items": [{"jp", "en",
"tiles": [canvas tile, ...] (left to right; top row tiles, the row below is +0x10), "align": "left"|"center"}]}.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / ".claude/skills/translate-retro-game/scripts")]
import font  # noqa: E402
import gfx_assets  # noqa: E402
import lz  # noqa: E402

SPEC = ROOT / "script/gfxtext.json"
# free space for recompressed blocks (all 0xFF in the original): file offset ranges
GFX_FREE = [(0x72000, 0x78000), (0x13AC40, 0x140000), (0xABC00, 0xB0000)]
INK, SHADOW = 3, 1


def glyph_rows(code):
    """16 rows of (ink bits, shadow bits) for a text code, width."""
    g = font.pack()[0][32 * code:32 * code + 32]
    rows = [(g[2 * y + 1], g[2 * y] & ~g[2 * y + 1] & 0xFF) for y in range(16)]
    return rows, font.widths().get(code, 0)


def strip(text, ntiles, align):
    """-> pixel rows (16 x ntiles*8) of palette indices."""
    from tbl import Table
    en = Table.load(ROOT / "tbl/en.tbl")
    codes = en.encode(text)
    width = sum(font.widths().get(c, 0) for c in codes)
    if width > ntiles * 8:
        raise ValueError(f"{text!r}: {width}px > {ntiles * 8}px")
    px = [[0] * (ntiles * 8) for _ in range(16)]
    x = (ntiles * 8 - width) // 2 if align == "center" else 1
    for c in codes:
        rows, w = glyph_rows(c)
        for y, (ink, sh) in enumerate(rows):
            for b in range(8):
                if x + b >= ntiles * 8:
                    continue
                if ink & (0x80 >> b):
                    px[y][x + b] = INK
                elif sh & (0x80 >> b):
                    px[y][x + b] = SHADOW
        x += w
    return px


def put_tile4(data, idx, px, x0, y0):
    """Write 8x8 pixels px[y0..][x0..] as a 4bpp tile at tile index idx."""
    t = bytearray(32)
    for y in range(8):
        for x in range(8):
            v = px[y0 + y][x0 + x]
            for p in range(4):
                if v & (1 << p):
                    t[(p // 2) * 16 + 2 * y + (p & 1)] |= 0x80 >> x
    data[idx * 32:idx * 32 + 32] = t


def tile2_px(data, t):
    b = data[t * 16:t * 16 + 16]
    return [[((b[2 * y] >> (7 - x)) & 1) | (((b[2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]


def apply_rows2(data, screen):
    """2bpp 8 px text rows (char-select bios): item = {"row", "half", "en"}; 8 tiles per half-row, condensed
    font, colour = the colour the Japanese used there."""
    import labels
    from collections import Counter
    for item in screen["items"]:
        first = item["row"] * 16 + item["half"] * 8
        old = Counter(v for t in range(first, first + 8) for r in tile2_px(data, t) for v in r if v)
        colour = old.most_common(1)[0][0] if old else 1
        text = item.get("en", "")
        w = labels.text_width(text)
        if w > 64:
            raise ValueError(f"{text!r}: {w}px > 64px")
        bits = labels.render(text) if text else bytes(64)
        # labels.render centres; bios are left-aligned: shift left by the centring offset
        shift = (64 - w) // 2 if text else 0
        rows = []
        for y in range(8):
            v = 0
            for t in range(8):
                v = (v << 8) | bits[t * 8 + y]
            rows.append((v << shift) & ((1 << 64) - 1))
        for t in range(8):
            tile = bytearray(16)
            for y in range(8):
                byte = (rows[y] >> (8 * (7 - t))) & 0xFF
                if colour & 1:
                    tile[2 * y] = byte
                if colour & 2:
                    tile[2 * y + 1] = byte
            data[(first + t) * 16:(first + t) * 16 + 16] = tile


def apply(rom_orig):
    """-> {block id: new decompressed bytes} for every block a spec item touches."""
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    out = {}
    for screen in spec["screens"]:
        if screen.get("type") == "rows2":
            bid = screen["block"]
            out.setdefault(bid, bytearray(lz.decompress(rom_orig, int(bid, 16))[0]))
            apply_rows2(out[bid], screen)
            continue
        blocks = {int(k, 16): v for k, v in screen["blocks"].items()}
        for item in screen["items"]:
            if not item.get("en"):
                continue
            tiles = item["tiles"]
            px = strip(item["en"], len(tiles), item.get("align", "left"))
            for k, t in enumerate(tiles):
                base = max(b for b in blocks if b <= t)
                bid = blocks[base]
                if bid not in out:
                    out[bid] = bytearray(lz.decompress(rom_orig, int(bid, 16))[0])
                put_tile4(out[bid], t - base, px, 8 * k, 0)
                put_tile4(out[bid], t - base + 0x10, px, 8 * k, 8)
    return out


def pack(rom, rom_orig):
    """Recompress changed blocks into GFX_FREE and repoint their loaders."""
    refs = {src: r for src, (_, _, r) in gfx_assets.assets().items()}
    cursor = [list(r) for r in GFX_FREE]
    for bid, data in apply(rom_orig).items():
        comp = lz.compress(bytes(data))
        for c in cursor:
            if c[0] + len(comp) <= c[1] and (c[0] >> 15) == ((c[0] + len(comp) - 1) >> 15):
                off = c[0]
                c[0] += len(comp)
                break
        else:
            raise ValueError(f"no free space for block {bid} ({len(comp)} bytes)")
        rom[off:off + len(comp)] = comp
        bank, addr = off >> 15, 0x8000 | (off & 0x7FFF)
        for r in refs[int(bid, 16)]:
            rom[r + 1:r + 4] = bytes([addr & 0xFF, addr >> 8, bank | (rom[r + 3] & 0x80)])


def preview():
    from PIL import Image
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    outdir = ROOT / "work/gfxtext"
    outdir.mkdir(parents=True, exist_ok=True)
    for bid, data in apply(rom).items():
        imgs = []
        for d in (lz.decompress(rom, int(bid, 16))[0], bytes(data)):
            n = len(d) // 32
            img = Image.new("L", (128, (n // 16) * 8))
            for t in range(n):
                for y in range(8):
                    for x in range(8):
                        v = sum(((d[t * 32 + (p // 2) * 16 + 2 * y + (p & 1)] >> (7 - x)) & 1) << p for p in range(4))
                        img.putpixel(((t % 16) * 8 + x, (t // 16) * 8 + y), v * 80 % 256)
            imgs.append(img)
        sheet = Image.new("L", (256 + 8, imgs[0].height), 40)
        sheet.paste(imgs[0], (0, 0))
        sheet.paste(imgs[1], (136, 0))
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(outdir / f"{bid}.png")
        print(outdir / f"{bid}.png")


if __name__ == "__main__":
    preview()
