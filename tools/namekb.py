"""High-score name entry keyboard (scene 0860D9, reached after a top-10 finish): English layout on both pages.
Input tables: 2 pages x 9 rows x 10 u16 main-font codes (high byte = dakuten flags) at 0x36B50 / 0x36C04.
Display: BG1 tilemap LZ 120812 (page p at rows 32p..; grid row r at tile row 3+2r, col 3+2c; right column
labels cols 25-29), tile = 0x100 + code in the 8x8 4bpp keyboard font LZ 11FB6C/11FE55/120215/120526 (64 codes
each; ink 1, shadow 2 right/below). Names are stored as main-font codes, so every key must be an EN font code.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import font8  # noqa: E402
import lz  # noqa: E402

TABLES = (0x36B50, 0x36C04)
MAP, FONT = "120812", {0x00: "11FB6C", 0x40: "11FE55"}
ATTR, BLANK = 0x2800, 0x2900
RIGHT, LEFT = 0x3C, 0x3D  # unused (box) codes in the keyboard font
GRID = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ", "abcdefghij", "klmnopqrst", "uvwxyz", "0123456789",
        ".,-!?+=/:~", ""]
# the ranking draws names with the JP 16x16 font (glyph = code): give it a-z on the EN lowercase codes
JPFONT, LOWER = 0x88000, (0x101, 0x61, 26)
# right column: tile row -> label (゛ ゜, カタカナ/ひらがな toggle, すすむ, もどる, けす, おわり)
LABELS = {9: "", 11: "", 13: [RIGHT], 15: [LEFT], 17: "Erase", 19: "Done"}
ARROWS = {RIGHT: "...#.... ....#... ######.. ....#... ...#....",
          LEFT: "..#..... .#...... ######.. .#...... ..#....."}


def codes(text):
    from tbl import Table
    en = Table.load(ROOT / "tbl/en.tbl")
    return list(text) if isinstance(text, list) else [en.encode(ch)[0] for ch in text]


def tile(rows):
    """8 bytes of 1bpp rows (bit 7 = left) -> 32-byte 4bpp tile, ink 1, shadow 2 right/below like the JP glyphs."""
    ink = lambda x, y: 0 <= x < 8 and 0 <= y < 8 and rows[y] >> (7 - x) & 1  # noqa: E731
    t = bytearray(32)
    for y in range(8):
        for x in range(8):
            v = 1 if ink(x, y) else 2 if ink(x - 1, y) or ink(x, y - 1) or ink(x - 1, y - 1) else 0
            for p in range(2):
                if v >> p & 1:
                    t[2 * y + p] |= 0x80 >> x
    return t


def blocks(rom_orig):
    """-> {block id: new decompressed bytes} (merged into gfxtext.apply)."""
    out = {b: bytearray(lz.decompress(rom_orig, int(b, 16))[0]) for b in (MAP, *FONT.values())}
    glyphs = {font8.CODE[ch]: font8.glyph(off, rows) for ch, (off, rows) in font8.G.items()}
    for c, s in ARROWS.items():
        glyphs[c] = bytes([0] + [int(r.replace(".", "0").replace("#", "1"), 2) for r in s.split()] + [0, 0])
    for c, rows in glyphs.items():
        base = max(b for b in FONT if b <= c)
        out[FONT[base]][32 * (c - base):32 * (c - base) + 32] = tile(rows)
    tm = out[MAP]
    put = lambda row, col, code: tm.__setitem__(slice(2 * (32 * row + col), 2 * (32 * row + col) + 2),  # noqa: E731
                                                (ATTR | 0x100 + code if code else BLANK).to_bytes(2, "little"))
    for page in (0, 32):
        for r in range(9):
            row = codes(GRID[r])
            for c in range(10):
                put(page + 3 + 2 * r, 3 + 2 * c, row[c] if c < len(row) else 0)
        for r, text in LABELS.items():
            lab = codes(text)
            for c in range(5):
                put(page + r, 25 + c, lab[c] if c < len(lab) else 0)
    return out


def pack(rom):
    """Write the input tables (both pages the same layout, no dakuten flags)."""
    data = b"".join((codes(GRID[r])[c] if c < len(GRID[r]) else 0).to_bytes(2, "little")
                    for r in range(9) for c in range(10))
    for t in TABLES:
        rom[t:t + len(data)] = data
    src, dst, n = LOWER
    rom[JPFONT + 64 * dst:JPFONT + 64 * (dst + n)] = rom[JPFONT + 64 * src:JPFONT + 64 * (src + n)]


RANGES = [(t, t + 179) for t in TABLES] + [(JPFONT + 64 * LOWER[1], JPFONT + 64 * (LOWER[1] + LOWER[2]) - 1)]

assert all(len(r) <= 10 for r in GRID) and len(GRID) == 9
