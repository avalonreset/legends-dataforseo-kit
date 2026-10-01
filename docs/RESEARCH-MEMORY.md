# Research memory handoff

Keep modules independent. `legends-dataforseo` collects and packages evidence;
Empire organizes durable knowledge; GeoGrid and other consumers interpret it.
No vault application, MCP server or additional runtime dependency is required.
These offline operations never collect new data or promote canonical findings.

## Explicit client workspace

Store research outside the tool installation, for example:

```text
client-workspace/
  requests/
  responses/
  evidence/
  findings/
```

The workspace is a user-selected directory, not a required vault application.
Use a stable, explicit client identity. Tool updates should not move or replace
client evidence. Directory selection is not permission to publish private data.

1. Save the complete original request/settings under `requests/`.
2. Add `--output client-workspace/responses/serp.json` to the reviewed collection
   command. It saves full JSON and prints a labelled summary. Existing files are
   refused before HTTP. Without `--output`, collection still prints full JSON;
   no new automatic capture or compact-output default is introduced.
3. Record the actual observation time. Do not substitute the later export time.
4. Export to the explicit evidence bank:

```sh
legends-dataforseo evidence export client-workspace/responses/serp.json client-workspace/evidence --workspace client-a --endpoint /serp/google/organic/live/advanced --request-file client-workspace/requests/serp.json --observed-at 2026-10-01T12:00:00Z
```

Use the exact original endpoint and request. Export accepts standard raw task
envelopes from this client or another authorized collector. Compact `.ai` views
and `wait` wrapper objects need an explicit adapter/extraction; they are not
silently normalized. Pending, empty and failed task responses remain evidence
of those states. Inputs are not secret-scanned: review credentials, account
information and out-of-scope private data before export. Keep packages private.

## Find, verify, view and reuse without another purchase

```sh
legends-dataforseo evidence inventory client-workspace/evidence --workspace client-a --endpoint /serp/google/organic/live/advanced --limit 25
legends-dataforseo evidence find client-workspace/evidence --query coffee --limit 25
legends-dataforseo evidence verify client-workspace/evidence/PACKAGE_ID
legends-dataforseo evidence view client-workspace/evidence/PACKAGE_ID --summary
legends-dataforseo evidence view client-workspace/evidence/PACKAGE_ID --select tasks.0.result.0.items --limit 3
legends-dataforseo evidence reuse client-workspace/evidence/PACKAGE_ID --workspace client-a --endpoint /serp/google/organic/live/advanced --request-file client-workspace/requests/serp.json --max-age-hours 24
```

The primary CLI, `python -m legends_dataforseo evidence`, and the existing
`python -m legends_dataforseo.evidence` module expose the same operations.
No credentials or network access are required. `reuse` exit 0 means eligible
for semantic review; exit 2 means ineligible and includes reasons. It never
refreshes, retries or buys a replacement. Optional `--now` permits an explicit
timezone-aware evaluation time for reproducible checks.

Inventory/search scans manifests, not raw responses or notes. It checks each
manifest's content-derived identity and reports `response_integrity=not_checked`.
A listed package might have a missing or modified response; run verify/view/reuse
before trusting it. `--workspace` and `--endpoint` are exact filters. `--query`
is case-insensitive substring search over metadata, including original request
settings, not semantic relevance scoring. Returned rows omit request bodies.

Inventory defaults to 50 entries, accepts 1 through 1000, and supports `--offset`
with `next_offset`. Scanning remains linear in the number of package directories;
there is no persistent database index. Errors are reported separately and bounded
by the same limit with an omitted count. Entry limits are not byte/token budgets:
manifest task arrays and strings may still be large. Manifests over 2 MB are
rejected during inventory. Repeated pagination over a changing bank is not a
transactional snapshot; callers should inspect `evidence_id` for duplicates.

View verifies complete evidence before deriving output. Without display flags it
returns the complete response. `--summary` retains every task ID/status/cost but
omits results. `--select` chooses dotted paths and `--limit` bounds displayed
lists, with omission counts. Strings are not truncated and summary task lists
are not capped. Saved raw bytes never change. Full verification reads the entire
response; a small display does not imply constant-memory parsing of large data.

## Integrity and compatibility

The create-only package contains byte-identical `response.json`, `manifest.json`
and a readable `README.md` intake note. Identity covers workspace, endpoint,
request/settings, observation time, producer, response hash and task/cost metadata.
New 0.1.3 packages also include `note_sha256`, binding exact README bytes. Older
v1 packages remain valid with `note_integrity=not_recorded`; their notes are not
silently claimed verified. Manifest/response checks and per-task metadata
cross-checks still apply. Hashes detect corruption, not false original metadata
or a hostile actor rewriting both data and hashes. This is not signed provenance.

Identical new exports reuse the verified package. A changed manifest or note
contract produces a new identity. Packages move between directories without
changing their identity, because package links are relative and identity excludes
storage paths. Interrupted exports fail verification; no automatic repair,
deletion or resubmission occurs. Symlinked package files are refused.

Reuse requires exact client, endpoint and request match, a caller-selected
freshness ceiling, successful task statuses and present results. Future/stale
observations are rejected. Empty result items can be genuine observations and
still require interpretation. Reported costs are snapshots, not incremental
charges. Do not sum repeated exports/polling receipts as separate purchases.

## Empire intake

1. Select the user's vault explicitly. Never use a product checkout as a vault.
2. Verify/review the bounded package inventory before staging under
   `inbox/research/PACKAGE_ID`; do not overwrite an existing intake.
3. Use the existing Empire capture and ingestion protocol. Capture source files
   immutably, preserve hashes and cite vault-relative source references.
4. Merge reviewed findings through the transaction protocol into the relevant
   business dossier and claim ledger. A captured package is not canonical truth.
5. Keep observations, hypotheses, actions and outcomes distinct; retain source
   dates and contradictions. Where apply is unavailable, leave a verified intake
   and explicit pending-merge receipt.

The package is attachable source material for multiple consumers. It does not
create business strategy, a knowledge graph, or accepted recommendations by
itself. No automatic canonical promotion, refresh scheduling or billing
reconciliation is introduced. GeoGrid keeps its own bank and public dependency
pin; export selected responses rather than copying whole private run directories.

## Measured offline navigation

One local synthetic run used 200 packages with approximately 64 KiB responses.
Inventory returned 25 entries in 1.7432 seconds and opened **zero raw responses**.
An 8,403,634-byte response produced a 659-byte explicitly selected view in 0.0658
seconds including integrity verification; all original bytes remained intact.
There were no provider calls. These are one-machine observations, not universal
throughput, memory or scalability guarantees. Reproduce with
`python scripts/benchmark_evidence.py`; output timing and temporary path length
can vary. Memory usage was not measured. Exact fixture includes 1000 result items
and an 8 MiB string, demonstrating that callers can select items without dumping
the unrelated large string into their context.
