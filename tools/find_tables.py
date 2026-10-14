"""Find 16-bit pointer tables (same LoROM bank) whose entries all point at E0-terminated kana strings.
    python -X utf8 tools/find_tables.py [--min 4]
A string start is a position after E0 (or FD) where >= 2 text codes run to the next E0.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rom = (ROOT / "rom/orig.sfc").read_bytes()
MIN = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 4


def is_text(b):
    return 0x41 <= b <= 0x93 or 0xA1 <= b <= 0xDF or 0x02 <= b <= 0x3F or b == 0


def string_at(o):
    """Length to E0 if bytes from o look like a name string, else 0."""
    n = 0
    while o + n < len(rom) and n < 40:
        b = rom[o + n]
        if b == 0xE0:
            return n if n >= 2 else 0
        if b in (0xFE, 0xFF):
            n += 2
        elif is_text(b):
            n += 1
        else:
            return 0
    return 0


for bank in range(0x40):
    base = bank * 0x8000
    blk = rom[base:base + 0x8000]
    starts = {o for o in range(1, 0x8000) if blk[o - 1] in (0xE0, 0xFD) and string_at(base + o)}
    o = 0
    while o < 0x7FFE:
        n = 0
        while o + 2 * n < 0x7FFE:
            p = struct.unpack_from("<H", blk, o + 2 * n)[0]
            if p >= 0x8000 and (p - 0x8000) in starts:
                n += 1
            else:
                break
        if n >= MIN:
            p0 = struct.unpack_from("<H", blk, o)[0]
            print(f"table {base + o:06X} bank {bank:02X} n={n} first-> {base + p0 - 0x8000:06X}")
            o += 2 * n
        else:
            o += 1
