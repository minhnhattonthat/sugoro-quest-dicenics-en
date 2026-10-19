"""English glyphs for the game's 8x8 1bpp font ($04:F49B, 8 bytes per code, bit 7 = left), used by the status panel's
equipment names (routine $07:AFEF). Codes 0x61-0x7A are kana in the JP font; the EN name codes put a-z there.
Glyphs are 5 px wide at x=1, x-height rows 2-6, ascenders from row 0, descenders to row 7.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 0x2749B

# rows top to bottom; the strings are aligned to the glyph's first row (given as offset)
G = {
    "a": (2, ".###. ....# .#### #...# .####"),
    "b": (0, "#.... #.... ####. #...# #...# #...# ####."),
    "c": (2, ".#### #.... #.... #.... .####"),
    "d": (0, "....# ....# .#### #...# #...# #...# .####"),
    "e": (2, ".###. #...# ##### #.... .####"),
    "f": (0, "..##. .#... ####. .#... .#... .#... .#..."),
    "g": (2, ".#### #...# #...# .#### ....# ####."),
    "h": (0, "#.... #.... ####. #...# #...# #...# #...#"),
    "i": (0, "..#.. ..... .##.. ..#.. ..#.. ..#.. .###."),
    "j": (0, "...#. ..... ..##. ...#. ...#. ...#. #..#. .##.."),
    "k": (0, "#.... #.... #..#. #.#.. ##... #.#.. #..#."),
    "l": (0, ".##.. ..#.. ..#.. ..#.. ..#.. ..#.. .###."),
    "m": (2, "##.#. #.#.# #.#.# #.#.# #.#.#"),
    "n": (2, "####. #...# #...# #...# #...#"),
    "o": (2, ".###. #...# #...# #...# .###."),
    "p": (2, "####. #...# #...# ####. #.... #...."),
    "q": (2, ".#### #...# #...# .#### ....# ....#"),
    "r": (2, "#.##. ##..# #.... #.... #...."),
    "s": (2, ".#### #.... .###. ....# ####."),
    "t": (0, ".#... .#... ####. .#... .#... .#..# ..##."),
    "u": (2, "#...# #...# #...# #..## .##.#"),
    "v": (2, "#...# #...# #...# .#.#. ..#.."),
    "w": (2, "#...# #...# #.#.# #.#.# .#.#."),
    "x": (2, "#...# .#.#. ..#.. .#.#. #...#"),
    "y": (2, "#...# #...# #...# .#### ....# .###."),
    "z": (2, "##### ...#. ..#.. .#... #####"),
    "'": (0, ".#... .#... .#... ..... ..... ..... ..... ....."),
}
CODE = {**{c: 0x61 + i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")}, "'": 0x5B}


def glyph(off, rows):
    out = [0] * 8
    for i, r in enumerate(rows.split()):
        out[off + i] = int(r.replace(".", "0").replace("#", "1"), 2) << 2
    return bytes(out)


def pack(rom):
    for ch, (off, rows) in G.items():
        rom[BASE + 8 * CODE[ch]: BASE + 8 * CODE[ch] + 8] = glyph(off, rows)


RANGE = (BASE + 8 * 0x5B, BASE + 8 * 0x7B - 1)


def cond_table():
    """256 x 8 bytes: condensed 3 px glyphs at bits 7-5 (left half of a cell; the routine shifts them for the right half)."""
    from labels import cond_glyphs
    from tbl import Table
    en = Table.load(ROOT / "tbl/en.tbl")
    tab = bytearray(8 * 256)
    for ch, rows in cond_glyphs().items():
        code = en.encode(ch)
        if len(code) == 1:
            for y, r in enumerate(rows):
                tab[8 * code[0] + y] = int(r.replace(".", "0").replace("#", "1"), 2) << 5
    return bytes(tab)
