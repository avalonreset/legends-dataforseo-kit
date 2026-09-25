# Research memory handoff

Keep the modules independent. DataForSEO collects evidence; legends-empire
organizes durable knowledge; GeoGrid and other consumers interpret it. No Hub,
vault application, MCP or new runtime dependency is required for this export.

## One package, multiple consumers

`python -m legends_dataforseo.evidence export response.json ./evidence --workspace client-id --endpoint /serp/google/organic/live/advanced --request-file request.json --observed-at 2026-09-22T12:00:00Z`

Use the actual recorded observation time and complete original request; never
substitute export time or invent missing settings. Accepts standard raw task
envelopes saved by the kit, official tooling, or another authorized collector.
Compact `.ai` views need a separate adapter; they are not silently normalized.
Review inputs for credentials, account details and out-of-scope private data.
This exporter is not a secret scanner. Store packages privately by default.

The create-only package contains the unchanged response, hashed manifest and a
readable intake note. Its identity includes workspace, endpoint, settings,
observation time and response hash. Identical exports reuse a verified package;
changed evidence creates another package. Partial writes fail verification and
must be reviewed; no automatic repair, deletion, submission or retry occurs.

`python -m legends_dataforseo.evidence verify ./evidence/PACKAGE_ID`

The Python `assess_reuse` function requires the target workspace, endpoint,
complete request and caller-selected freshness limit. Matching successful
evidence is eligible for semantic review, not automatically authoritative.
Empty result items may be genuine observations; interpret them by endpoint.
Pending/error task statuses remain intact and do not become reusable findings.
Reported costs are snapshots; do not sum repeated polling/export costs.

## legends-empire intake

1. Select the user's vault explicitly. Never use a product checkout as a vault.
2. Verify and review the bounded package inventory before staging it under
   `inbox/research/PACKAGE_ID`. Do not overwrite an existing intake.
3. Use legends-empire's existing capture plan/apply and wiki-ingest recipe.
   Capture raw files immutably, preserve hashes, and cite vault-relative sources.
4. Merge findings through its transaction protocol, linking the appropriate
   business dossier and source/claim ledgers. An intake is not a canonical merge.
5. Keep observations, hypotheses, proposed actions and measured outcomes distinct.
   Retain contradictions and source dates. Deduplicate by source identity.

Do not bypass platform restrictions in the vault transaction engine. Where apply
is unavailable, leave a verified intake and a clear pending-merge receipt.

## GeoGrid and other consumers

GeoGrid keeps its existing bank and public dependency pin. Export selected
provider responses using their saved settings and timestamps; preserve study
and parent-run identifiers in downstream notes. Do not copy an entire customer
run folder, rebank reports as independent purchases, or introduce a second HTTP
client. Other consumers can read exactly the same package without GeoGrid.

## Acceptance boundary

This first slice implements offline export, integrity checks and conservative
reuse eligibility. It does not yet automate vault transactions, schedule fresh
research, deduplicate billing across tasks, or restore queued jobs. Existing
collection and wait APIs remain unchanged. Validate these next steps separately
before claiming end-to-end research-memory automation.
