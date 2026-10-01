"""Synthetic offline benchmark of manifest inventory and full-response views."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

from legends_dataforseo.evidence import export, inventory, view


def run(packages=200, response_kib=64, large_mib=8):
    if not 1 <= packages <= 2000 or not 1 <= response_kib <= 1024 or not 1 <= large_mib <= 64:
        raise ValueError("bounded synthetic benchmark sizes required")
    with tempfile.TemporaryDirectory(prefix="legends-evidence-benchmark-") as temporary:
        root = Path(temporary)
        source = root / "source.json"
        bank = root / "bank"
        source.write_bytes(json.dumps({"status_code": 20000, "cost": 0, "tasks": [{"id": "synthetic", "status_code": 20000, "cost": 0, "result": [{"items": [{"text": "x" * (response_kib * 1024)}]}]}]}).encode())
        stamp = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        for index in range(packages):
            export(source, bank, workspace="synthetic-client", endpoint="/serp/google/organic/live/advanced", request=[{"keyword": f"synthetic-{index}"}], observed_at=stamp)
        export_seconds = time.perf_counter() - start
        raw_reads = 0
        original_text, original_bytes = Path.read_text, Path.read_bytes
        def read_text(path, *a, **kw):
            nonlocal raw_reads
            if path.name == "response.json": raw_reads += 1
            return original_text(path, *a, **kw)
        def read_bytes(path, *a, **kw):
            nonlocal raw_reads
            if path.name == "response.json": raw_reads += 1
            return original_bytes(path, *a, **kw)
        with patch.object(Path, "read_text", read_text), patch.object(Path, "read_bytes", read_bytes):
            start = time.perf_counter()
            listing = inventory(bank, workspace="synthetic-client", limit=25)
            inventory_seconds = time.perf_counter() - start
        large = {"status_code": 20000, "cost": 0, "tasks": [{"id": "synthetic-large", "status_code": 20000, "result": [{"items": [{"rank": n} for n in range(1000)], "large_text": "x" * (large_mib * 1024 * 1024)}]}]}
        raw = json.dumps(large).encode()
        source.write_bytes(raw)
        package = export(source, bank, workspace="synthetic-client", endpoint="/serp/google/organic/live/advanced", request=[{"keyword": "large-synthetic"}], observed_at=stamp)
        start = time.perf_counter()
        selected = view(package, select=["tasks.0.result.0.items"], limit=3)
        view_seconds = time.perf_counter() - start
        assert (package / "response.json").read_bytes() == raw
        assert raw_reads == 0 and listing["matches"] == packages
        return {"synthetic": True, "provider_calls": 0, "packages": packages,
            "response_kib": response_kib, "export_seconds": round(export_seconds, 4),
            "inventory_seconds": round(inventory_seconds, 4), "inventory_raw_file_reads": raw_reads,
            "inventory_returned": len(listing["items"]), "inventory_json_bytes": len(json.dumps(listing).encode()),
            "large_response_bytes": len(raw), "selected_view_bytes": len(json.dumps(selected).encode()),
            "verified_view_seconds": round(view_seconds, 4), "original_raw_bytes_preserved": True,
            "limits": "One local synthetic run; not a throughput SLA. Inventory scans all manifests, bounds returned entries. View verification reads complete raw evidence."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", type=int, default=200)
    parser.add_argument("--response-kib", type=int, default=64)
    parser.add_argument("--large-mib", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(run(args.packages, args.response_kib, args.large_mib), indent=2)
    if args.output:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(report + "\n")
    print(report)
