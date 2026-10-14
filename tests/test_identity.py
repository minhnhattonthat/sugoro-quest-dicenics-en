"""Identity build: repacking the extracted Japanese must reproduce the original ROM byte for byte."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools")]
import build  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ORIG.exists(), reason="needs rom/orig.sfc")


def test_identity_build():
    assert build.build(identity=True) == build.ORIG.read_bytes()
