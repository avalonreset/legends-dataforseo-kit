# Changelog

## 0.4.0 — 2026-09-21

- Official documentation discovery, endpoint reading, search, and an offline cache.
- Save full responses with `--output`; inspect local JSON with summary, selection,
  and list limits without another provider request.
- Optional bounded GET polling of saved queue IDs, preserving original envelopes
  and reporting incomplete cost information.
- Explicit `.ai` endpoint support without changing standard paths or responses.
- Stronger failure handling: POST ambiguity flag, sanitized HTTP protocol errors,
  rejected task IDs retained in CLI output, and nonfatal ledger warnings.
- Dated upstream comparison and a read-only official-version check.

The existing `api_request` signatures and standard task status behavior remain
compatible with 0.3.x. No provider package or runtime dependency was added.

## 0.3.1 — 2026-09-21

- Legends banner, live badges, and matching social-preview artwork.
- Wheel-first quick start with verified output; installation, CLI, and first-request guides.
- Contributor guidance, issue forms, pull request template, and private security-reporting path.
- Searchable package metadata, documentation links, and branded source distribution.
- Repeatable checksum preparation and downloadable CI build artifacts.

The Python request signatures and transport behavior are unchanged from 0.3.0.
Existing immutable dependency pins continue to work.

## 0.3.0 — 2026-09-20

Initial public release.

- Portable Python package and JSON CLI; no runtime dependencies.
- Stable api_request transport, named serp/demand/maps helpers, and route registry.
- Maps live and standard queue POST/GET contracts; original task statuses retained.
- Environment-only credentials, redirects blocked, no automatic retries/failover.
- Explicit paid confirmation and advisory per-request budget prechecks.
- Offline examples and tests; cross-platform CI; MIT license and source provenance.

Operational limits: local estimates are not price guarantees; queue polling
and aggregate budgets belong to the caller. No PyPI upload, private account
routing, workstation-specific installer, or full first-class wrapper for every
DataForSEO endpoint. Use confirmed generic calls for documented v3 endpoints.
