"""Offline evidence navigation and compatibility contracts."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from legends_dataforseo import cli
from legends_dataforseo import evidence

REQ = [{"keyword": "synthetic coffee", "location_code": 2840}]
STAMP = "2026-10-01T00:00:00Z"
ENDPOINT = "/serp/google/organic/live/advanced"


def package(tmp_path, workspace="client-a", status=20000):
    source = tmp_path / "raw.json"
    source.write_bytes(json.dumps({"status_code": 20000, "cost": 0,
        "tasks": [{"id": "synthetic", "status_code": status, "cost": 0,
                   "result": [{"items": [{"rank": n} for n in range(20)]}]}]}, indent=3).encode())
    return evidence.export(source, tmp_path / "bank", workspace=workspace,
                           endpoint=ENDPOINT, request=REQ, observed_at=STAMP)


def test_new_note_bound_and_original_bytes_preserved(tmp_path):
    root = package(tmp_path)
    assert (root / "response.json").read_bytes() == (tmp_path / "raw.json").read_bytes()
    assert evidence.verify(root)["note_integrity"] == "verified"
    (root / "README.md").write_text("tampered")
    with pytest.raises(ValueError, match="note integrity"):
        evidence.verify(root)


def test_legacy_note_not_recorded_remains_explicit(tmp_path):
    root = package(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text())
    del manifest["note_sha256"]
    del manifest["evidence_id"]
    manifest["evidence_id"] = hashlib.sha256(evidence._json(manifest).encode()).hexdigest()
    (root / "manifest.json").write_text(evidence._json(manifest))
    (root / "README.md").write_text("old notes can change without an old stored hash")
    assert evidence.verify(root)["note_integrity"] == "not_recorded"


def test_inventory_reads_manifests_without_opening_raw_or_notes(tmp_path, monkeypatch):
    package(tmp_path)
    package(tmp_path, "client-b")
    original_text, original_bytes = Path.read_text, Path.read_bytes
    def text(path, *a, **kw):
        assert path.name not in ("response.json", "README.md")
        return original_text(path, *a, **kw)
    def raw(path, *a, **kw):
        assert path.name not in ("response.json", "README.md")
        return original_bytes(path, *a, **kw)
    monkeypatch.setattr(Path, "read_text", text)
    monkeypatch.setattr(Path, "read_bytes", raw)
    listing = evidence.inventory(tmp_path / "bank", query="coffee", limit=1)
    assert listing["matches"] == 2
    assert len(listing["items"]) == 1
    assert listing["next_offset"] == 1
    assert listing["response_integrity"] == "not_checked"
    assert evidence.inventory(tmp_path / "bank", workspace="client-b")["matches"] == 1


def test_inventory_does_not_confuse_metadata_with_complete_integrity(tmp_path):
    root = package(tmp_path)
    (root / "response.json").write_text("broken")
    assert evidence.inventory(root.parent)["matches"] == 1
    with pytest.raises(ValueError): evidence.view(root, summary=True)


def test_corrupt_inventory_entries_reported_bounded(tmp_path):
    root = package(tmp_path)
    for n in range(3):
        broken = root.parent / f"bad-{n}"
        broken.mkdir()
        (broken / "manifest.json").write_text("null")
    report = evidence.inventory(root.parent, limit=1)
    assert len(report["items"]) == 1
    assert len(report["errors"]) == 1
    assert report["errors_omitted"] == 2


@pytest.mark.parametrize("opts", [{"limit": 0}, {"limit": 1001}, {"offset": -1}, {"query": " "}])
def test_invalid_inventory_bounds(tmp_path, opts):
    with pytest.raises(ValueError): evidence.inventory(tmp_path, **opts)


def test_view_full_by_default_and_selected_view_preserves_raw(tmp_path):
    root = package(tmp_path)
    before = (root / "response.json").read_bytes()
    full = evidence.view(root)
    assert len(full["response_view"]["tasks"][0]["result"][0]["items"]) == 20
    view = evidence.view(root, select=["tasks.0.result.0.items"], limit=2)
    assert len(view["response_view"]["selected"]["tasks.0.result.0.items"]) == 2
    assert view["response_view"]["omitted_items"]["tasks.0.result.0.items"] == 18
    assert (root / "response.json").read_bytes() == before


def test_reuse_primary_cli_success_then_stale_and_mismatched(tmp_path, capsys):
    root = package(tmp_path)
    request = tmp_path / "request.json"
    request.write_text(json.dumps(REQ))
    args = ["evidence", "reuse", str(root), "--workspace", "client-a", "--endpoint", ENDPOINT,
            "--request-file", str(request), "--max-age-hours", "24", "--now", "2026-10-01T12:00:00Z"]
    assert cli.main(args) == 0
    assert json.loads(capsys.readouterr().out)["requires_semantic_review"] is True
    args[-1] = "2026-10-03T00:00:00Z"
    assert cli.main(args) == 2
    assert "future or stale observation" in json.loads(capsys.readouterr().out)["reasons"]


def test_primary_cli_inventory_and_missing_file_error(tmp_path, capsys):
    root = package(tmp_path)
    assert cli.main(["evidence", "find", str(root.parent), "--query", "coffee"]) == 0
    assert json.loads(capsys.readouterr().out)["matches"] == 1
    assert cli.main(["evidence", "verify", str(tmp_path / "absent")]) == 2
    error = capsys.readouterr()
    assert "Traceback" not in error.err
    assert json.loads(error.err)["error"] == "EvidenceError"


def test_moved_package_still_verifies(tmp_path):
    root = package(tmp_path)
    moved = tmp_path / "separate-client-workspace"
    root.rename(moved)
    assert evidence.verify(moved)["workspace"] == "client-a"


@pytest.mark.parametrize("raw", [
    b'{"status_code":20000,"status_code":20000,"tasks":[]}',
    b'{"status_code":20000,"tasks":[{"result":[{"nested":NaN}]}]}',
    b'{"status_code":20000,"tasks":[{"result":[{"nested":Infinity}]}]}',
    b'{"status_code":20000,"tasks":[{"result":[{"nested":1e999}]}]}'
])
def test_export_rejects_ambiguous_json_without_changing_source(tmp_path, raw):
    source = tmp_path / "ambiguous.json"
    source.write_bytes(raw)
    with pytest.raises(ValueError):
        evidence.export(source, tmp_path / "bank", workspace="client-a", endpoint=ENDPOINT,
                        request=REQ, observed_at=STAMP)
    assert source.read_bytes() == raw
    assert not (tmp_path / "bank").exists()


def test_cli_rejects_duplicate_request_keys_cleanly(tmp_path, capsys):
    root = package(tmp_path)
    request = tmp_path / "request.json"
    request.write_text('[{"keyword":"one","keyword":"two"}]')
    code = evidence.main(["reuse", str(root), "--workspace", "client-a", "--endpoint", ENDPOINT,
                          "--request-file", str(request), "--max-age-hours", "24"])
    assert code == 2
    assert "Traceback" not in capsys.readouterr().err


def test_linked_ancestor_rejected_by_inventory_and_verify(tmp_path):
    root = package(tmp_path)
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(root.parent, target_is_directory=True)
    except OSError:
        pytest.skip("symlink privilege unavailable")
    with pytest.raises(ValueError, match="linked"):
        evidence.inventory(alias)
    with pytest.raises(ValueError, match="linked"):
        evidence.verify(alias / root.name)
