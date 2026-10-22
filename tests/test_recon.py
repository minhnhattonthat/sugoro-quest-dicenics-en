"""Recon invariants on the original ROM: table roundtrip over the whole main script, LZSS codec."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skill  # noqa: E402,F401  (puts the skill's scripts/ on sys.path)
from tbl import Table  # noqa: E402
import lz  # noqa: E402
import script  # noqa: E402

ROM_PATH = ROOT / "rom/orig.sfc"
pytestmark = pytest.mark.skipif(not ROM_PATH.exists(), reason="needs rom/orig.sfc")


@pytest.fixture(scope="module")
def rom():
    return ROM_PATH.read_bytes()


def test_script_roundtrip(rom):
    t = Table.load(ROOT / "tbl/jp.tbl")
    n = 0
    for g, bank, off, ptrs in script.groups(rom):
        for p in set(ptrs):
            o = script.lorom(bank, p)
            text, used = t.decode(rom, o)
            assert "[" not in text, (g, hex(o), text)
            assert t.encode(text) == rom[o:o + used], (g, hex(o))
            n += 1
    assert n > 600


def test_lz_roundtrip(rom):
    data, used = lz.decompress(rom, 0x1177A3)
    assert len(data) == 0x1000
    assert lz.decompress(lz.compress(data[:0x300]))[0] == data[:0x300]
