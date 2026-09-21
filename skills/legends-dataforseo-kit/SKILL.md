---
name: legends-dataforseo-kit
description: Install and operate the agent-neutral DataForSEO Python package and CLI for SERP, Maps, keyword research, and queued scans.
---

# legends-dataforseo-kit

Read ../../README.md and ../../docs/API.md. Install a pinned release into the
consumer environment. Run `legends-dataforseo doctor`, then
`legends-dataforseo routes`. No MCP or agent-specific integration is needed.

Use `serp`, `maps`, and `demand` for offline request previews. For standard Maps
queues, use `api_request('/serp/google/maps/task_post', tasks, confirm=True)`
after the caller approves execution and budget. Poll the returned ID with GET
`/serp/google/maps/task_get/advanced/{id}`; preserve all task statuses.

Use only environment credentials. Missing credentials should lead to secret
manager setup guidance, never a request to paste credentials into chat.
`doctor --live` is a sanitized no-charge authentication check.

Paid CLI execution requires `--execute`, `--estimated-cost-usd`, and
`--max-cost-usd`. These carry explicit authorization without another prompt.
Estimates are advisory. Reconcile actual response cost. Never automatically
retry a paid call after a timeout or API error.
