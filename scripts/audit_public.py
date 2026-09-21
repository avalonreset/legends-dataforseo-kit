"""Scan tracked source and built archives for forbidden private artifacts."""

import re
import subprocess
import tarfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
checks = []
for name in filter(None, tracked):
    checks.append((name, (root / name).read_bytes()))
for archive in (root / "dist").glob("*"):
    if archive.suffix == ".whl":
        with zipfile.ZipFile(archive) as opened:
            checks.extend((name, opened.read(name)) for name in opened.namelist())
    elif archive.name.endswith(".tar.gz"):
        with tarfile.open(archive) as opened:
            checks.extend((member.name, opened.extractfile(member).read())
                          for member in opened.getmembers() if member.isfile())

# Construct private-pattern terms without embedding a workstation path.
patterns = [
    re.compile(rb"[A-Za-z]:" + rb"[\\/]" + rb"(?:Users|legends|empire)", re.I),
    re.compile(rb"-----BEGIN " + rb"(?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(rb"gh[pousr]_" + rb"[A-Za-z0-9]{30,}"),
    re.compile(rb"github_pat_" + rb"[A-Za-z0-9_]{30,}"),
]
failures = []
for name, content in checks:
    parts = Path(name).parts
    if any(p in {"var", ".env", ".git", "__pycache__", ".codex", ".claude"} for p in parts):
        failures.append(name + ": private artifact path")
    if any(pattern.search(content) for pattern in patterns):
        failures.append(name + ": private content pattern")
if failures:
    raise SystemExit("Public audit failed:\n" + "\n".join(failures))
print(f"public source/archive audit PASS ({len(checks)} entries)")
