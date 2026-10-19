"""Status panel page 2: the baked-in "ダイスマン n号" lines (OBJ tiles in the 0x69000 sheet: top and bottom half of one sprite row) -> "Diceman No." in condensed glyphs.
Two 96x8 strips (tile lists below, 4bpp, bg colour 14, ink 15); the digit tile (index 9) and the icon tiles stay as is.
"""
from labels import cond_glyphs

L1 = [0x8C, 0x8D, 0x8E, 0x8F, 0xAC, 0xAD, 0xAE, 0xAF, 0xCC, 0xCD, 0xCE, 0xCF]
L2 = [0x9C, 0x9D, 0x9E, 0x9F, 0xBC, 0xBD, 0xBE, 0xBF, 0xDC, 0xDD, 0xDE, 0xDF]
TEXT, X0, BG, INK = "Diceman No.", 24, 14, 15
KEEP = (0, 1, 9)


def off(t):
    return 0x69800 + 32 * t if t < 0x20 else 0x69000 + 32 * t


def put(rom, o, y, bits):
    """bits = 8 booleans (left to right) for row y of the tile at o."""
    for p in range(4):
        m = sum((1 << (7 - x)) for x, b in enumerate(bits) if ((INK if b else BG) >> p) & 1)
        rom[o + (16 if p > 1 else 0) + 2 * y + (p & 1)] = m


def pack(rom):
    g = cond_glyphs()
    rows = [[False] * 96 for _ in range(8)]
    x = X0
    for ch in TEXT:
        for y, r in enumerate(g[ch]):
            for dx, c in enumerate(r):
                rows[y][x + dx] = c == "#"
        x += 4
    for ts in (L1, L2):
        for i, t in enumerate(ts):
            if i not in KEEP:
                for y in range(8):
                    put(rom, off(t), y, rows[y][i * 8:i * 8 + 8])


RANGES = [(off(t), off(t) + 31) for ts in (L1, L2) for i, t in enumerate(ts) if i not in KEEP]
