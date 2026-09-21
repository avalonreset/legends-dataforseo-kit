"""Install the built wheel into a clean venv and exercise the installed surface."""

import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
wheel, = (root / "dist").glob("*.whl")
with tempfile.TemporaryDirectory() as directory:
    target = Path(directory)
    venv.EnvBuilder(with_pip=True).create(target / "venv")
    python = target / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], check=True)
    code = "from importlib.metadata import version; from legends_dataforseo import *; assert __version__ == version('legends-dataforseo-kit'); assert load_routes()['version'] == __version__; assert route_for('maps-task-post')['method'] == 'POST'; print('installed wheel API PASS')"
    subprocess.run([str(python), "-I", "-c", code], cwd=target, check=True)
    subprocess.run([str(python), "-I", "-m", "legends_dataforseo", "routes"], cwd=target, check=True, stdout=subprocess.DEVNULL)
    subprocess.run([str(python), "-I", "-m", "legends_dataforseo", "serp", "example"], cwd=target, check=True, stdout=subprocess.DEVNULL)
print("clean wheel smoke PASS")
