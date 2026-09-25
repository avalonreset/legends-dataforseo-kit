# Changelog

## 0.1.0 - 2026-09-25

- Router-native generation reset: one registered skill (`cto-legends`) with a pinned copy vendored at `skills/cto-legends/SKILL.md` (router commit 6975dcbf073e5eec7a30ce6a04a6975238c61158); per-module skill registration removed; version reset to 0.1.0 with history preserved.

## 0.5.0 - 2026-09-23

- Ship the offline research-evidence module required by Legends Obsidian intake.
- Export immutable raw responses with workspace, request settings, source time,
  task statuses, reported costs and content identity.
- Verify package integrity; assess reuse against workspace, settings and freshness.
- Preserve pending, empty and failed responses without treating them as findings.
- Test the handoff from the installed wheel, without credentials or paid calls.

The Python transport contract is unchanged. Vault ingestion remains an explicit
Legends Obsidian transaction, not an automatic side effect of export.

## 0.4.0 - 2026-09-21

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

## 0.3.1 - 2026-09-21

- Legends banner, live badges, and matching social-preview artwork.
- Wheel-first quick start with verified output; installation, CLI, and first-request guides.
- Contributor guidance, issue forms, pull request template, and private security-reporting path.
- Searchable package metadata, documentation links, and branded source distribution.
- Repeatable checksum preparation and downloadable CI build artifacts.

The Python request signatures and transport behavior are unchanged from 0.3.0.
Existing immutable dependency pins continue to work.

## 0.3.0 - 2026-09-20

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
