"""Build the patched ROM.
    python -X utf8 tools/build.py [--identity] [--out build/sq_en.sfc]
--identity: repack the Japanese script in place with no other change; must equal the original (tests/test_identity.py).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import text  # noqa: E402

ORIG = ROOT / "rom/orig.sfc"


def build(identity=False):
    rom = bytearray(ORIG.read_bytes())
    groups = text.load_groups()
    if identity:
        for g, entries in groups.items():
            text.write_group(rom, g, entries, lambda e: text.JP.encode(e["jp"]))
        return bytes(rom)
    raise SystemExit("English build not implemented yet")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "build/sq_en.sfc"))
    a = ap.parse_args()
    data = build(a.identity)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(out, "identical to original" if data == ORIG.read_bytes() else "differs from original")


if __name__ == "__main__":
    main()
