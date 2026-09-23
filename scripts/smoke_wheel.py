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
    payload = target / "synthetic.json"
    payload.write_text('{"status_code":20000,"cost":0,"tasks":[{"id":"synthetic","status_code":40601}]}', encoding="utf-8")
    subprocess.run([str(python), "-I", "-m", "legends_dataforseo", "view", str(payload), "--summary"], cwd=target, check=True, stdout=subprocess.DEVNULL)
    subprocess.run([str(python), "-I", "-m", "legends_dataforseo", "wait", "/serp/google/maps/task_get/advanced/synthetic"], cwd=target, check=True, stdout=subprocess.DEVNULL)
    subprocess.run([str(python), "-I", "-c", "from legends_dataforseo import docs_search, docs_read, wait_task, response_view; assert response_view({'id':'synthetic','status_code':20000}, summary=True)['summary']['id']=='synthetic'"], cwd=target, check=True)
    request = target / "request.json"
    request.write_text('[{"keyword":"synthetic","location_code":2840,"language_code":"en"}]', encoding="utf-8")
    package = subprocess.check_output([str(python), "-I", "-m", "legends_dataforseo.evidence", "export", str(payload), str(target / "evidence"), "--workspace", "synthetic-client", "--endpoint", "/serp/google/organic/live/advanced", "--request-file", str(request), "--observed-at", "2026-09-23T00:00:00Z"], cwd=target, text=True).strip()
    subprocess.run([str(python), "-I", "-m", "legends_dataforseo.evidence", "verify", package], cwd=target, check=True)
    subprocess.run([str(python), "-I", "-c", "import sys; from legends_dataforseo.evidence import assess_reuse; assert not assess_reuse(sys.argv[1], workspace='different-client', endpoint='/serp/google/organic/live/advanced', request=[{'keyword':'synthetic'}], max_age_hours=24)['eligible']", package], cwd=target, check=True)
print("clean wheel smoke PASS")
