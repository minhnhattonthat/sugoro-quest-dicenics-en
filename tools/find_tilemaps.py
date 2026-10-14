"""Find tilemap runs (>= MIN consecutive incrementing 16-bit entries, same attributes) in the ROM and in
decompressed blocks (work/gfx/*.bin). Prints source, offset, first entry, run length.
    python -X utf8 tools/find_tilemaps.py [--min 6] [--lo 0x100 --hi 0x3FF]
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
arg = dict(zip(sys.argv[1::2], sys.argv[2::2]))
MIN = int(arg.get("--min", 6))
LO, HI = int(arg.get("--lo", "0x100"), 16), int(arg.get("--hi", "0x3FF"), 16)


def runs(data, name):
    for par in (0, 1):
        n = len(data) // 2 - 1
        k = par
        while k < len(data) - 2 * MIN:
            w = struct.unpack_from("<H", data, k)[0]
            t = w & 0x3FF
            if LO <= t <= HI:
                m = 1
                while k + 2 * m + 1 < len(data) and struct.unpack_from("<H", data, k + 2 * m)[0] == w + m:
                    m += 1
                if m >= MIN:
                    print(f"{name} {k:06X} {w:04X} x{m}")
                    k += 2 * m
                    continue
            k += 2


runs((ROOT / "rom/orig.sfc").read_bytes(), "rom")
for f in sorted((ROOT / "work/gfx").glob("*.bin")):
    runs(f.read_bytes(), f.stem)
