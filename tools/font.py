"""English VWF font: font/vwf.txt art -> 256 glyph slots indexed by text code (see tbl/en.tbl), 8x16 2bpp.
Glyph = 16 rows x (plane0, plane1), bit 7 = leftmost pixel. Ink = colour 3, drop shadow (right, down) = colour 1.
Width = art width (advance incl. 1 px spacing).
    python -X utf8 tools/font.py [OUT_DIR]      # OUT_DIR/en_font.bin (8 KB), OUT_DIR/en_widths.bin (256)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "font" / "vwf.txt"

# code -> art char. Uppercase, digits and punctuation keep the game's own codes, so strings the game builds
# (numbers, "1P") still render; lowercase sits on the (unused in English) hiragana codes 0x61-0x7A.
CODES = {0x00: " ", 0x02: ",", 0x03: ".", 0x04: ",", 0x05: ".", 0x06: "·", 0x07: ":", 0x08: "~", 0x09: "?",
         0x0A: "!", 0x0B: "…", 0x0C: "-", 0x1B: "♥", 0x0D: "=", 0x0E: "+", 0x0F: "/", 0x1C: '"', 0x1D: '"', 0x1E: "'",
         0x1F: "'", 0x5B: "'", 0x5C: '"', 0x5D: "(", 0x5E: ")", 0x5F: "&", 0x60: "%", 0x7B: "#", 0x7C: "*",
         0x7D: ";", 0x7E: "<", 0x7F: ">", 0x80: "[", 0x81: "]", 0x82: "$", 0x83: "@", 0x84: "^", 0x85: "`",
         0x86: "\\"}
CODES.update({0x10 + i: str(i) for i in range(10)})
CODES.update({0x21 + i: chr(0x41 + i) for i in range(26)})
CODES.update({0x61 + i: chr(0x61 + i) for i in range(26)})


def parse(text=None):
    """-> {char: [16 row strings]}"""
    glyphs, cur = {}, None
    for line in (text or ART.read_text(encoding="utf-8")).splitlines():
        if line.startswith("char "):
            name = line[5:]
            cur = " " if name == "space" else name
            assert len(cur) == 1, line
            glyphs[cur] = []
        elif line and set(line) <= {".", "#"} and cur is not None:
            glyphs[cur].append(line)
    for ch, rows in glyphs.items():
        assert len(rows) == 16 and len(set(map(len, rows))) == 1 and len(rows[0]) <= 8, ch
    return glyphs


def glyph_bytes(rows):
    ink = [sum(0x80 >> x for x, c in enumerate(r) if c == "#") for r in rows]
    out = bytearray()
    for y in range(16):
        up = ink[y - 1] if y else 0
        shadow = ((ink[y] >> 1) | up | (up >> 1)) & ~ink[y] & 0xFF
        out += bytes([ink[y] | shadow, ink[y]])  # colour 3 = both planes, colour 1 = plane 0 only
    return bytes(out)


def widths():
    """code -> advance px"""
    g = parse()
    return {code: len(g[ch][0]) for code, ch in CODES.items()}


def pack():
    g = parse()
    font, wid = bytearray(32 * 256), bytearray(256)
    for code, ch in CODES.items():
        font[32 * code:32 * code + 32] = glyph_bytes(g[ch])
        wid[code] = len(g[ch][0])
    return bytes(font), bytes(wid)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build"
    out.mkdir(parents=True, exist_ok=True)
    font, wid = pack()
    (out / "en_font.bin").write_bytes(font)
    (out / "en_widths.bin").write_bytes(wid)
    print(out / "en_font.bin", len(font), "bytes")


if __name__ == "__main__":
    main()
