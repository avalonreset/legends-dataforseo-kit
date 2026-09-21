# Changelog

## 0.3.0 — 2026-09-20

First public early release, following the local 0.3 development series.

- Portable Python package and JSON CLI; no runtime dependencies.
- Stable api_request transport, named serp/demand/maps helpers, and route registry.
- Maps live and standard queue POST/GET contracts; original task statuses retained.
- Environment-only credentials, redirects blocked, no automatic retries/failover.
- Explicit paid confirmation and advisory per-request budget prechecks.
- Offline examples and tests; cross-platform CI; MIT license and source provenance.

Early-release limits: local estimates are not price guarantees; queue polling
and aggregate budgets belong to the caller. No PyPI upload, private account
routing, workstation-specific installer, or full first-class wrapper for every
DataForSEO endpoint. Use confirmed generic calls for documented v3 endpoints.
