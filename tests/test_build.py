"""Build the English ROM and check what the game will actually read: every main-script pointer and every name
pointer decodes (en.tbl) to the English in script/, the VWF hook is in, and nothing outside the allowed ranges
changed."""
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill  # noqa: E402
import build  # noqa: E402
import names  # noqa: E402
import script  # noqa: E402
import text  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ORIG.exists() or not build.ASAR.exists(), reason="needs ROM + asar")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("b") / "sq_en.sfc"
    return build.build(out=out)


def test_script_pointers(built):
    for g, entries in text.load_groups().items():
        ptr, bank = struct.unpack_from("<HB", built, script.GROUP_TABLE + 3 * g)
        base = script.lorom(bank, ptr)
        by_id = {e["id"]: e for e in entries}
        for i, e in enumerate(entries):
            src = by_id[e.get("same", e["id"])]
            p = struct.unpack_from("<H", built, base + 2 * i)[0]
            got = build.EN.decode(built, script.lorom(bank, p))[0]
            assert got == src["en"], (e["id"], got, src["en"])


def test_name_pointers(built):
    for e in names.load():
        bank = int(e["id"][1:3], 16)
        for s in e["slots"]:
            o = names.lorom(bank, struct.unpack_from("<H", built, s)[0])
            end = built.index(b"\xE0", o)
            assert build.EN.decode(built, o, end - o)[0] == e["en"], e["id"]


def test_vwf_hook(built):
    assert built[0x40121:0x40125] != bytes.fromhex("22818208")


def test_romdiff(built, tmp_path):
    out = tmp_path / "b.sfc"
    out.write_bytes(built)
    ranges = [ln.split("#")[0].strip() for ln in (ROOT / "tools/allowed_ranges.txt").read_text().splitlines()]
    r = subprocess.run([sys.executable, "-X", "utf8", str(skill.SCRIPTS / "romdiff.py"),
                        str(build.ORIG), str(out), *[x for x in ranges if x]], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
