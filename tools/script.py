"""Main script: message id = group<<12 | index. Group table $08:848A (3 bytes: ptr16, bank) for groups 0-7;
each group is a table of 16-bit pointers into its own bank, ending where the first string begins.
    python -X utf8 tools/script.py stats|show GROUP [FROM [N]]
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill  # noqa: E402,F401  (puts the skill's scripts/ on sys.path)
from tbl import Table  # noqa: E402

GROUP_TABLE = 0x4048A
NGROUPS = 8


def lorom(bank, addr):
    return ((bank & 0x7F) << 15) | (addr & 0x7FFF)


def groups(rom):
    """[(group, bank, table_off, [ptr16...])]"""
    out = []
    for g in range(NGROUPS):
        ptr, bank = struct.unpack_from("<HB", rom, GROUP_TABLE + 3 * g)
        off = lorom(bank, ptr)
        ptrs = []
        first = 0x10000
        while ptr + 2 * len(ptrs) < first:
            p = struct.unpack_from("<H", rom, off + 2 * len(ptrs))[0]
            ptrs.append(p)
            if p < 0x8000:
                raise ValueError(f"group {g}: bad pointer {p:04X} at slot {len(ptrs) - 1}")
            first = min(first, p)
        out.append((g, bank, off, ptrs))
    return out


def main():
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    t = Table.load(ROOT / "tbl/jp.tbl")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    for g, bank, off, ptrs in groups(rom):
        if cmd == "stats":
            ends = [lorom(bank, p) + t.decode(rom, lorom(bank, p))[1] for p in ptrs]
            print(f"group {g}: bank {bank:02X} table {off:06X} n={len(ptrs)} text {lorom(bank, min(ptrs)):06X}-{max(ends):06X}")
        elif cmd == "show" and g == int(sys.argv[2]):
            a = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
            n = int(sys.argv[4], 0) if len(sys.argv) > 4 else len(ptrs)
            for i in range(a, min(a + n, len(ptrs))):
                print(f"{g:X}{i:03X} {lorom(bank, ptrs[i]):06X} {t.decode(rom, lorom(bank, ptrs[i]))[0]}")


if __name__ == "__main__":
    main()
