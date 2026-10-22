"""Main script dump/pack. script/gN.json: one entry per pointer slot of group N:
  {"id": "7005", "jp": ..., "en": "", "same": "7004"?}   same = slot reuses that id's string (pointer shared).
    python -X utf8 tools/text.py dump [--force]       # writes only missing files unless --force
    python -X utf8 tools/text.py stats
pack(rom, entries_by_group, field) is used by build.py; packing JP in place reproduces the original bytes.
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill  # noqa: E402,F401  (puts the skill's scripts/ on sys.path)
from tbl import Table  # noqa: E402
import script  # noqa: E402

SCRIPT = ROOT / "script"
JP = Table.load(ROOT / "tbl/jp.tbl")


def load_groups():
    return {g: json.loads((SCRIPT / f"g{g}.json").read_text(encoding="utf-8")) for g in range(script.NGROUPS)}


def save(path, entries):
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def dump(rom, force=False):
    SCRIPT.mkdir(exist_ok=True)
    for g, bank, off, ptrs in script.groups(rom):
        path = SCRIPT / f"g{g}.json"
        if path.exists() and not force:
            print(f"skip {path.name} (exists; --force overwrites English)")
            continue
        first, entries = {}, []
        for i, p in enumerate(ptrs):
            eid = f"{g:X}{i:03X}"
            if p in first:
                entries.append({"id": eid, "same": first[p]})
                continue
            first[p] = eid
            entries.append({"id": eid, "jp": JP.decode(rom, script.lorom(bank, p))[0], "en": ""})
        save(path, entries)
        print(f"{path.name}: {len(entries)} slots, {len(first)} strings")


def encode_group(entries, pick):
    """-> (ptr offsets relative to string area start, string blob). pick(entry) returns the bytes of one string."""
    rel, blob = {}, bytearray()
    for e in entries:
        if "same" in e:
            continue
        rel[e["id"]] = len(blob)
        blob += pick(e)
    return [rel[e.get("same", e["id"])] for e in entries], bytes(blob)


def write_group(rom, g, entries, pick, bank=None, addr=None):
    """Write pointer table + strings for group g at bank:addr (default: original place) and update the group table.
    Returns the end file offset."""
    gbank = rom[script.GROUP_TABLE + 3 * g + 2]
    gaddr = struct.unpack_from("<H", rom, script.GROUP_TABLE + 3 * g)[0]
    bank, addr = (gbank, gaddr) if bank is None else (bank, addr)
    rels, blob = encode_group(entries, pick)
    strings = addr + 2 * len(entries)
    end = strings + len(blob)
    if end > 0x10000:
        raise ValueError(f"group {g} overflows bank {bank:02X} at {addr:04X} (+{end - 0x10000:#x} bytes)")
    off = script.lorom(bank, addr)
    for i, r in enumerate(rels):
        struct.pack_into("<H", rom, off + 2 * i, strings + r)
    rom[off + 2 * len(entries):off + 2 * len(entries) + len(blob)] = blob
    struct.pack_into("<HB", rom, script.GROUP_TABLE + 3 * g, addr, bank)
    return off + 2 * len(entries) + len(blob)


def main():
    rom = (ROOT / "rom/orig.sfc").read_bytes()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "dump":
        dump(rom, "--force" in sys.argv)
    elif cmd == "refresh":  # re-decode every jp field (after a jp.tbl fix), keeping en
        for g, bank, off, ptrs in script.groups(rom):
            path = SCRIPT / f"g{g}.json"
            entries = json.loads(path.read_text(encoding="utf-8"))
            for e, p in zip(entries, ptrs):
                if "same" not in e:
                    e["jp"] = JP.decode(rom, script.lorom(bank, p))[0]
            save(path, entries)
        print("jp refreshed")
    elif cmd == "stats":
        tot = done = 0
        for g, entries in load_groups().items():
            s = [e for e in entries if "same" not in e]
            d = sum(1 for e in s if e["en"])
            tot, done = tot + len(s), done + d
            print(f"g{g}: {d}/{len(s)}")
        print(f"total {done}/{tot}")


if __name__ == "__main__":
    main()
