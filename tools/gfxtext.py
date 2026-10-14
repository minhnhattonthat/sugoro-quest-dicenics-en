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


def strip(text, ntiles, align, style=None):
    """-> pixel rows (16 x ntiles*8) of palette indices. style "header": options-screen title font
    (outline 6, body A/4/5 top to bottom)."""
    from tbl import Table
    en = Table.load(ROOT / "tbl/en.tbl")
    codes = en.encode(text.strip()) if text.strip() else b""
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
                elif sh & (0x80 >> b) and style != "header":
                    px[y][x + b] = SHADOW
        x += w
    if style == "header":
        ink = [[v == INK for v in row] for row in px]
        for y in range(16):
            for x in range(ntiles * 8):
                if ink[y][x]:
                    px[y][x] = 0xA if y <= 5 else 0x4 if y <= 9 else 0x5
                elif any(0 <= y + dy < 16 and 0 <= x + dx < ntiles * 8 and ink[y + dy][x + dx]
                         for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    px[y][x] = 0x6
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


def apply_lines2(data, screen):
    """2bpp, 16 tiles wide; item = {"y": pixel top, "half": 0/1, "en", "clear": [y0, y1]} - clears pixel rows
    y0..y1 of that half, then draws the condensed-font line at y (colour = most common colour cleared)."""
    import labels
    from collections import Counter

    def loc(x, y):
        r, yy = divmod(y, 8)
        return (r * 16 + x // 8) * 16 + 2 * yy, 0x80 >> (x % 8)

    for item in screen["items"]:
        x0 = item["half"] * 64
        y0, y1 = item["clear"]
        seen = Counter()
        for y in range(y0, y1 + 1):
            for x in range(x0, x0 + 64):
                i, m = loc(x, y)
                v = (1 if data[i] & m else 0) | (2 if data[i + 1] & m else 0)
                if v:
                    seen[v] += 1
                data[i] &= ~m & 0xFF
                data[i + 1] &= ~m & 0xFF
        colour = seen.most_common(1)[0][0] if seen else 1
        text = item["en"]
        w = labels.text_width(text)
        if w > 64:
            raise ValueError(f"{text!r}: {w}px > 64px")
        bits = labels.render(text)
        shift = (64 - w) // 2
        for yy in range(8):
            row = 0
            for t in range(8):
                row = (row << 8) | bits[t * 8 + yy]
            row = (row << shift) & ((1 << 64) - 1)
            for c in range(64):
                if row & (1 << (63 - c)):
                    i, m = loc(x0 + c, item["y"] + yy)
                    if colour & 1:
                        data[i] |= m
                    if colour & 2:
                        data[i + 1] |= m


def apply_boxes4(data, screen):
    """4bpp block, 16 tiles wide. item = {"rect": [x0, y0, x1, y1] interior in block pixels (inclusive),
    "lines": [en..]}: every pixel of the interior becomes the interior's most common colour (the box fill), then
    the lines are drawn centred in the VWF font, ink = the most common other colour (the old text)."""
    from collections import Counter
    from tbl import Table
    en = Table.load(ROOT / "tbl/en.tbl")

    def loc(x, y):
        return (y // 8) * 16 + x // 8, x % 8, y % 8

    def get(x, y):
        t, px, py = loc(x, y)
        return sum(((data[t * 32 + (p // 2) * 16 + 2 * py + (p & 1)] >> (7 - px)) & 1) << p for p in range(4))

    def put(x, y, v):
        t, px, py = loc(x, y)
        for p in range(4):
            i = t * 32 + (p // 2) * 16 + 2 * py + (p & 1)
            data[i] = (data[i] | (0x80 >> px)) if v & (1 << p) else (data[i] & ~(0x80 >> px) & 0xFF)

    for item in screen["items"]:
        x0, y0, x1, y1 = item["rect"]
        c = Counter(get(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)).most_common()
        fill, ink = c[0][0], (c[1][0] if len(c) > 1 else 1)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                put(x, y, fill)
        n = len(item["lines"])
        h = y1 - y0 + 1
        if item.get("font") == "cond":
            import labels
            for li, text in enumerate(item["lines"]):
                w = labels.text_width(text)
                if w > x1 - x0 + 1:
                    raise ValueError(f"{text!r}: {w}px > {x1 - x0 + 1}px")
                bits = labels.render(text)
                top = y0 + (h - 9 * n) // 2 + 9 * li
                for yy in range(8):
                    for t in range(8):
                        for b in range(8):
                            if bits[t * 8 + yy] & (0x80 >> b):
                                x = x0 + (x1 - x0 + 1 - 64) // 2 + t * 8 + b
                                if x0 <= x <= x1 and y0 <= top + yy <= y1:
                                    put(x, top + yy, ink)
            continue
        for li, text in enumerate(item["lines"]):
            codes = en.encode(text)
            w = sum(font.widths().get(k, 0) for k in codes)
            if w > x1 - x0 + 1:
                raise ValueError(f"{text!r}: {w}px > {x1 - x0 + 1}px")
            x = x0 + (x1 - x0 + 1 - w) // 2
            top = y0 + (h - 12 * n) // 2 + 12 * li - 3  # glyph rows 3..14 hold the ink
            for k in codes:
                rows, gw = glyph_rows(k)
                for yy, (inkb, _) in enumerate(rows):
                    for b in range(8):
                        if inkb & (0x80 >> b) and y0 <= top + yy <= y1 and x + b <= x1:
                            put(x + b, top + yy, ink)
                x += gw


def apply(rom_orig):
    """-> {block id: new decompressed bytes} for every block a spec item touches."""
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    out = {}
    for screen in spec["screens"]:
        if screen.get("type") == "rulewin":
            import rulewin
            out.update(rulewin.apply(rom_orig, screen))
            continue
        if screen.get("type") == "boxes4":
            bid = screen["block"]
            out.setdefault(bid, bytearray(lz.decompress(rom_orig, int(bid, 16))[0]))
            apply_boxes4(out[bid], screen)
            continue
        if screen.get("type") in ("rows2", "lines2"):
            bid = screen["block"]
            out.setdefault(bid, bytearray(lz.decompress(rom_orig, int(bid, 16))[0]))
            (apply_rows2 if screen["type"] == "rows2" else apply_lines2)(out[bid], screen)
            continue
        blocks = {int(k, 16): v for k, v in screen["blocks"].items()}
        for item in screen["items"]:
            if not item.get("en"):
                continue
            tiles = item["tiles"]
            px = strip(item["en"], len(tiles), item.get("align", "left"), item.get("style"))
            for k, t in enumerate(tiles):
                base = max(b for b in blocks if b <= t)
                bid = blocks[base]
                if bid not in out:
                    out[bid] = bytearray(lz.decompress(rom_orig, int(bid, 16))[0])
                put_tile4(out[bid], t - base, px, 8 * k, 0)
                put_tile4(out[bid], t - base + 0x10, px, 8 * k, 8)
            m = item.get("map")
            if m:  # point the screen's tilemap rows at this item's tiles (32-entry rows, words)
                if m["block"] not in out:
                    out[m["block"]] = bytearray(lz.decompress(rom_orig, int(m["block"], 16))[0])
                tm = out[m["block"]]
                for c in range(m["width"]):
                    for dr, add in ((0, 0), (1, 0x10)):
                        o = 2 * ((m["row"] + dr) * 32 + m["col"] + c)
                        word = (m["attr"] | (tiles[c] + add)) if c < len(tiles) else m["blank"]
                        tm[o:o + 2] = word.to_bytes(2, "little")
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
