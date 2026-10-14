"""Find text-like regions: 64-byte windows where most bytes are kana codes (41-93 hira, A1-DF kata) or FE/FF/E0/FC/FD.
    python -X utf8 tools/scan_text.py [--min 0.7]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rom = (ROOT / "rom/orig.sfc").read_bytes()
thr = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 0.7
good = bytes(1 if (0x41 <= b <= 0x93 or 0xA1 <= b <= 0xDF or b in (0, 0xE0, 0xFC, 0xFD, 0xFE, 0xFF, 0x0B, 0x02, 0x03)) else 0
             for b in range(256))
W = 64
runs, start = [], None
for o in range(0, len(rom) - W, W):
    s = sum(good[b] for b in rom[o:o + W]) / W
    # flat runs of one byte are padding, not text
    if s >= thr and len(set(rom[o:o + W])) > 12:
        start = o if start is None else start
    elif start is not None:
        runs.append((start, o)); start = None
for a, b in runs:
    print(f"{a:06X}-{b:06X} {b - a:6d}")
print(len(runs), "regions", sum(b - a for a, b in runs), "bytes")
