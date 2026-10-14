"""Word spans in a 4bpp block of 16-px text bands (16 tiles wide, band = tile rows 2b and 2b+1).
    python -X utf8 tools/spans.py BLOCK [GAP]   -> per band: runs of tile columns with ink (split at GAP empty cols)
Ink = any pixel != 0 in the column of 8x16 pixels.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import strips  # noqa: E402


def spans(data, gap=1):
    out = []
    for b in range(len(data) // 32 // 32):
        cols = [any(strips.px4(data, (2 * b + h) * 16 + t, x, y) for h in (0, 1) for x in range(8) for y in range(8))
                for t in range(16)]
        runs, t = [], 0
        while t < 16:
            if cols[t]:
                a = t
                while t < 16 and (cols[t] or (t + gap <= 16 and any(cols[t:t + gap + 1]) and t > a)):
                    if not cols[t] and not any(cols[t + 1:t + 1 + gap]):
                        break
                    t += 1
                runs.append((a, t - a))
            else:
                t += 1
        out.append(runs)
    return out


if __name__ == "__main__":
    d = strips.block(sys.argv[1])
    for b, r in enumerate(spans(d, int(sys.argv[2]) if len(sys.argv) > 2 else 0)):
        print(b, r)
