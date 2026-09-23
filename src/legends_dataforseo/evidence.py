"""Offline evidence handoff. No provider calls or canonical vault mutations."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "legends-research-evidence/v1"


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False)


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _date(value):
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ValueError("observation time requires timezone")
    return date


def export(response, destination, *, workspace, endpoint, request, observed_at,
           producer="legends-dataforseo-kit"):
    """Bank one standard response with explicit scope; never infer collection time."""
    if not isinstance(workspace, str) or not workspace.strip():
        raise ValueError("explicit client/workspace identity required")
    if not endpoint.startswith("/") or any(x in endpoint for x in ("?", "#", ":", "..")):
        raise ValueError("endpoint must be a v3-relative path without query credentials")
    if not isinstance(request, (list, dict)) or not request:
        raise ValueError("full original request/settings required")
    _date(observed_at)
    raw = Path(response).read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("standard task envelope required; compact views are not raw evidence")
    if any(not isinstance(t, dict) for t in data["tasks"]):
        raise ValueError("invalid task envelope")
    manifest = dict(schema=SCHEMA, workspace=workspace, endpoint=endpoint,
                    request=request, observed_at=observed_at, producer=producer,
                    response_sha256=_hash(raw), status_code=data.get("status_code"),
                    reported_response_cost=data.get("cost"),
                    tasks=[{k: t.get(k) for k in ("id", "status_code", "cost")} for t in data["tasks"]])
    identity = _hash(_json(manifest).encode())
    manifest["evidence_id"] = identity
    target = Path(destination) / identity
    if target.exists():
        verify(target)
        return target
    target.mkdir(parents=True, exist_ok=False)
    # Exclusive writes: interrupted exports remain detectable, never silently repaired.
    with (target / "response.json").open("xb") as f:
        f.write(raw)
    with (target / "manifest.json").open("x", encoding="utf-8") as f:
        f.write(_json(manifest))
    text = ("# Research evidence\n\n"
            "Unreviewed source material; not an accepted finding or recommendation.\n\n"
            f"Observed: {observed_at}\n\n"
            "[Settings, task IDs and reported costs](manifest.json) · "
            "[Complete provider response](response.json)\n\n"
            "Costs are snapshots, not incremental charges. Do not sum repeated task receipts.\n"
            "Use the explicit workspace and complete request settings when considering reuse.\n"
            "Pending, empty and error responses are evidence of those states, not completed research.\n"
            "For Legends Obsidian: stage in the selected vault inbox, capture immutably, "
            "then ingest through the existing transaction protocol.\n")
    with (target / "README.md").open("x", encoding="utf-8") as f:
        f.write(text)
    return target


def verify(package):
    root = Path(package)
    if root.is_symlink():
        raise ValueError("linked evidence package")
    for name in ("manifest.json", "response.json", "README.md"):
        if (root / name).is_symlink() or not (root / name).is_file():
            raise ValueError("incomplete or linked evidence package")
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    identity = m.pop("evidence_id")
    if m.get("schema") != SCHEMA or _hash(_json(m).encode()) != identity:
        raise ValueError("manifest integrity mismatch")
    if _hash((root / "response.json").read_bytes()) != m["response_sha256"]:
        raise ValueError("response integrity mismatch")
    raw = json.loads((root / "response.json").read_bytes())
    expected_tasks = [{k: t.get(k) for k in ("id", "status_code", "cost")}
                      for t in raw["tasks"]]
    if (m["tasks"] != expected_tasks or m["status_code"] != raw.get("status_code")
            or m["reported_response_cost"] != raw.get("cost")):
        raise ValueError("manifest metadata differs from raw response")
    return dict(m, evidence_id=identity)


def assess_reuse(package, *, workspace, endpoint, request, max_age_hours, now=None):
    """Conservative eligibility, not permission to spend or proof of semantic relevance."""
    if not math.isfinite(max_age_hours) or max_age_hours < 0:
        raise ValueError("finite nonnegative freshness limit required")
    m = verify(package)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now requires timezone")
    reasons = []
    for key, value in (("workspace", workspace), ("endpoint", endpoint), ("request", request)):
        if m[key] != value:
            reasons.append(key + " differs")
    age = (current - _date(m["observed_at"])).total_seconds() / 3600
    if age < 0 or age > max_age_hours:
        reasons.append("future or stale observation")
    if m["status_code"] != 20000 or not m["tasks"] or any(t["status_code"] != 20000 for t in m["tasks"]):
        reasons.append("response is not fully successful")
    raw = json.loads((Path(package) / "response.json").read_bytes())
    if any(not t.get("result") for t in raw["tasks"]):
        reasons.append("result absent; review empty evidence separately")
    return dict(eligible=not reasons, reasons=reasons, evidence_id=m["evidence_id"],
                requires_semantic_review=True, provider_calls=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    save = sub.add_parser("export")
    save.add_argument("response")
    save.add_argument("destination")
    for name in ("workspace", "endpoint", "request-file", "observed-at"):
        save.add_argument("--" + name, required=True)
    check = sub.add_parser("verify")
    check.add_argument("package")
    args = parser.parse_args()
    if args.command == "verify":
        result = verify(args.package)
        print(_json({"verified": True, "evidence_id": result["evidence_id"]}))
    else:
        request = json.loads(Path(args.request_file).read_text(encoding="utf-8-sig"))
        print(export(args.response, args.destination, workspace=args.workspace,
                     endpoint=args.endpoint, request=request, observed_at=args.observed_at))


if __name__ == "__main__":
    main()
