"""Name lists (E0-terminated strings reached through 16-bit pointers in their own bank).
    python -X utf8 tools/names.py dump [--force]     # script/names.json (one entry per string)
    python -X utf8 tools/names.py coverage           # strings in each region not reached by a known slot
Each entry: {"id": "N04_92A3", "jp", "en", "slots": [file offsets of pointer slots]}.
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / ".claude/skills/translate-retro-game/scripts")]
from tbl import Table  # noqa: E402

JP = Table.load(ROOT / "tbl/jp.tbl")
PATH = ROOT / "script/names.json"

# region: bank, [start, end) file offsets of the original strings, extra free space usable for English
REGIONS = {
    0x04: {"text": [(0x212A3, 0x21704)], "free": [(0x27C9B, 0x28000)]},
    0x06: {"text": [(0x3312D, 0x3326E)], "free": [(0x37994, 0x38000)]},
    0x08: {"text": [(0x40772, 0x40AA7), (0x40B97, 0x40C69)], "free": [(0x43056, 0x48000)]},
}
# pointer slot sets: (bank, first slot offset, count, stride)
SLOTS = [
    (0x04, 0x21DB4, 12, 2),     # characters + stat dice
    (0x04, 0x21708, 118, 8),    # item / spell records, name at +0
    (0x06, 0x333F0, 39, 2),     # key items
    (0x08, 0x40AE3, 90, 2),     # weapons / armour / shields
    (0x08, 0x40C87, 27, 2),     # monsters
]


def lorom(bank, addr):
    return ((bank & 0x7F) << 15) | (addr & 0x7FFF)


def slots(rom):
    """{string file offset: [slot offsets]}"""
    out = {}
    for bank, first, n, stride in SLOTS:
        for i in range(n):
            s = first + i * stride
            out.setdefault(lorom(bank, struct.unpack_from("<H", rom, s)[0]), []).append(s)
    return out


def str_end(rom, off):
    """Offset of the E0 terminator (FE/FF xx are 2-byte glyphs: FE E0 is ム, not an end)."""
    while rom[off] != 0xE0:
        off += 2 if rom[off] in (0xFE, 0xFF) else 1
    return off


def decode(rom, off):
    return JP.decode(rom, off, length=str_end(rom, off) - off)[0]


def dump(rom, force=False):
    if PATH.exists() and not force:
        raise SystemExit(f"{PATH.name} exists (--force overwrites English)")
    entries = []
    for off, sl in sorted(slots(rom).items()):
        bank = (off >> 15) & 0x7F
        entries.append({"id": f"N{bank:02X}_{(off & 0x7FFF) | 0x8000:04X}", "jp": decode(rom, off), "en": "",
                        "slots": sl})
    PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{PATH.name}: {len(entries)} strings")


def coverage(rom):
    reached = slots(rom)
    for bank, r in REGIONS.items():
        missing = []
        for a, b in r["text"]:
            o = a
            while o < b:
                e = str_end(rom, o)
                if o not in reached:
                    missing.append(f"{o:06X} {decode(rom, o)}")
                o = e + 1
        print(f"bank {bank:02X}: {len(missing)} strings not reached by a known slot")
        for m in missing:
            print("  ", m)


KEEP = [(0x2158D, 0x21594)]  # クエストオフ: no known pointer, left untouched in case code points at it directly
MAX_BYTES = 21               # run-time copy buffers are 0x16 bytes including the E0


def pools(bank):
    r = REGIONS[bank]
    out = []
    for a, b in r["text"] + r["free"]:
        for ka, kb in KEEP:
            if a <= ka < b:
                out += [(a, ka), (kb, b)]
                break
        else:
            out.append((a, b))
    return out


def pack(rom, entries, pick):
    """Write every entry's bytes (pick(e) -> bytes without E0) into its bank's pools; repoint all slots.
    Identical strings share one copy. Clears the old string areas to 0xFF first."""
    for bank, r in REGIONS.items():
        for a, b in r["text"]:
            for ka, kb in KEEP:
                if a <= ka < b:
                    rom[a:ka] = b"\xFF" * (ka - a)
                    rom[kb:b] = b"\xFF" * (b - kb)
                    break
            else:
                rom[a:b] = b"\xFF" * (b - a)
    cursor = {bank: [list(p) for p in pools(bank)] for bank in REGIONS}
    placed = {}
    for e in entries:
        data = pick(e) + b"\xE0"
        if len(data) - 1 > MAX_BYTES:
            raise ValueError(f"{e['id']}: {len(data) - 1} bytes > {MAX_BYTES}")
        bank = int(e["id"][1:3], 16)
        key = (bank, data)
        if key not in placed:
            for p in cursor[bank]:
                if p[0] + len(data) <= p[1]:
                    placed[key] = p[0]
                    rom[p[0]:p[0] + len(data)] = data
                    p[0] += len(data)
                    break
            else:
                raise ValueError(f"bank {bank:02X} name space full at {e['id']}")
        for s in e["slots"]:
            struct.pack_into("<H", rom, s, (placed[key] & 0x7FFF) | 0x8000)


def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def main():
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "coverage"
    if cmd == "dump":
        dump(rom, "--force" in sys.argv)
    else:
        coverage(rom)


if __name__ == "__main__":
    main()
