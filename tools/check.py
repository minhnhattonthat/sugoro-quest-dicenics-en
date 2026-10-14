"""One-command check: pytest tests/ (+ text lint once it exists). The pre-commit hook runs this."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

steps = [[sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")],
         [sys.executable, "-X", "utf8", str(ROOT / "tools/lint.py")]]
for cmd in steps:
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(r.returncode)
print("check: ok")
