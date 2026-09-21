"""Write SHA-256 checksums for one wheel and sdist in dist/."""

import hashlib
from pathlib import Path

dist = Path(__file__).resolve().parents[1] / "dist"
wheels = sorted(dist.glob("*.whl"))
sources = sorted(dist.glob("*.tar.gz"))
if len(wheels) != 1 or len(sources) != 1:
    raise SystemExit("Expected exactly one wheel and one sdist in dist/.")
artifacts = wheels + sources
lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts]
(dist / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")
print("SHA256SUMS.txt written for wheel and sdist")
