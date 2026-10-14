import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent.parent / "tools")]
import lint  # noqa: E402


def entry(jp, en):
    return {"id": "7000", "jp": jp, "en": en}


def test_ok():
    assert lint.lint_entry(entry("{clr}あいう{nl}えお{key}{end}", "{clr}Hello there.{nl}Bye.{key}{end}")) == []


def test_errors():
    errs = lint.lint_entry(entry("{clr}あいう{key}{end}", "{clr}Hi{nl}two lines{end}"))
    assert any("control codes" in e for e in errs)
    assert any("lines > JP" in e for e in errs)
    assert any("px >" in e for e in lint.lint_entry(entry("{clr}あ{end}", "{clr}" + "M" * 40 + "{end}")))
    assert any("ordinal" in e for e in lint.lint_entry(entry("{v1}番{end}", "{v1}st{end}")))
    assert lint.line_px("{at11}No") == 11 * 12 + lint.line_px("No")
