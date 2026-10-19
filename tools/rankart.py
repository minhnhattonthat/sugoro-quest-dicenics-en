"""In-game rank screen: names (cyan italics) and "ポイント" are raw 4bpp tiles in the sheet at 0xA9000 (16 tiles per row).
Names: 6-tile spans (two per 2-tile-high row pair), outline 6 / body 9 like the end-game ranking.
"""
import gfxtext

BASE = 0xA9000
# (first tile row, first column, tiles wide, text, style)
ITEMS = [(8, 0, 6, "Pritz", "outline:9:6"), (8, 6, 6, "Cynthia", "outline:9:6"),
         (10, 0, 6, "Tanguy", "outline:9:6"), (10, 6, 6, "Dechtel", "outline:9:6"),
         (12, 0, 6, "Ulrik", "outline:9:6"), (12, 6, 6, "Diana", "outline:9:6"),
         (6, 12, 4, "Points", "outline:B:6")]


def pack(rom):
    sheet = bytearray(rom[BASE:BASE + 0x2000])
    for r, c, n, text, style in ITEMS:
        px = gfxtext.strip(text, n, "left", style)
        for k in range(n):
            for h in (0, 1):
                gfxtext.put_tile4(sheet, (r + h) * 16 + c + k, px, k * 8, h * 8)
    rom[BASE:BASE + 0x2000] = sheet


RANGES = [(BASE + 32 * ((r + h) * 16 + c), BASE + 32 * ((r + h) * 16 + c + n) - 1)
          for r, c, n, _, _ in ITEMS for h in (0, 1)]
