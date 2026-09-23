import json
from datetime import datetime, timezone

import pytest

from legends_dataforseo.evidence import export, verify, assess_reuse

STAMP = "2026-09-22T12:00:00+00:00"
NOW = datetime(2026, 9, 23, tzinfo=timezone.utc)
REQUEST = [{"keyword": "coffee", "location_code": 2840, "language_code": "en", "depth": 10}]


def make(tmp_path, status=20000, result=None):
    source = tmp_path / "saved.json"
    source.write_text(json.dumps({"status_code": 20000, "cost": 0.002,
        "tasks": [{"id": "saved-task", "status_code": status, "cost": 0.002,
                   "result": [{"items": []}] if result is None else result}]}))
    return export(source, tmp_path / "bank", workspace="client-a", endpoint="/serp/google/organic/live/advanced",
                  request=REQUEST, observed_at=STAMP)


def assess(path, **overrides):
    args = dict(workspace="client-a", endpoint="/serp/google/organic/live/advanced",
                request=REQUEST, max_age_hours=24, now=NOW)
    args.update(overrides)
    return assess_reuse(path, **args)


def test_roundtrip_and_idempotence(tmp_path):
    path = make(tmp_path)
    assert make(tmp_path) == path
    assert verify(path)["tasks"][0]["id"] == "saved-task"
    assert (path / "response.json").read_bytes() == (tmp_path / "saved.json").read_bytes()
    assert assess(path)["eligible"]


@pytest.mark.parametrize("override", [dict(workspace="other-client"), dict(max_age_hours=1),
    dict(endpoint="/other"), dict(request=[dict(REQUEST[0], language_code="de")]),
    dict(request=[dict(REQUEST[0], depth=100)]),
    dict(now=datetime(2026, 9, 20, tzinfo=timezone.utc))])
def test_incompatible_reuse(tmp_path, override):
    assert not assess(make(tmp_path), **override)["eligible"]


@pytest.mark.parametrize("status", [20100, 40601, 40102])
def test_pending_empty_error_are_preserved_not_reused(tmp_path, status):
    path = make(tmp_path, status)
    assert verify(path)["tasks"][0]["status_code"] == status
    assert not assess(path)["eligible"]


def test_missing_result(tmp_path):
    assert not assess(make(tmp_path, result=[]))["eligible"]


@pytest.mark.parametrize("filename", ["response.json", "manifest.json"])
def test_tampering(tmp_path, filename):
    path = make(tmp_path)
    (path / filename).write_text("{}")
    with pytest.raises((ValueError, KeyError)):
        verify(path)


def test_interrupted_package_not_silently_repaired(tmp_path):
    path = make(tmp_path)
    (path / "README.md").unlink()
    with pytest.raises(ValueError, match="incomplete"):
        make(tmp_path)


def test_no_duplicate_charge_claim(tmp_path):
    path = make(tmp_path)
    assert verify(path)["reported_response_cost"] == 0.002
    assert "not incremental charges" in (path / "README.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("limit", [-1, float("nan"), float("inf")])
def test_invalid_freshness(tmp_path, limit):
    with pytest.raises(ValueError):
        assess(make(tmp_path), max_age_hours=limit)


def test_manifest_summary_must_match_raw_even_with_recomputed_identity(tmp_path):
    import hashlib
    path = make(tmp_path, status=40601)
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    del manifest["evidence_id"]
    manifest["tasks"][0]["status_code"] = 20000
    manifest["evidence_id"] = hashlib.sha256(json.dumps(manifest, sort_keys=True,
        ensure_ascii=False, indent=2, allow_nan=False).encode()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="metadata differs"):
        verify(path)


def test_whitespace_workspace_rejected_before_export(tmp_path):
    with pytest.raises(ValueError, match="workspace"):
        export(tmp_path / "missing.json", tmp_path / "bank", workspace="  ",
               endpoint="/test", request=[{}], observed_at=STAMP)
