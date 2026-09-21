# Agent instructions

This project is agent-neutral. Use Python and the CLI directly; no MCP server
or particular coding agent is required.

1. Read README.md and docs/API.md before changing the public contract.
2. Run `legends-dataforseo doctor` and `legends-dataforseo routes`.
3. Run `python -m pytest` for changes; tests must stay offline by default.
4. Preserve raw task envelopes for pending, empty, and failed tasks. Never retry
   a paid request automatically or hide a returned task ID.
5. Preview paid work and respect the user's existing execution authorization
   and budget. Pass confirm=True after review; do not add redundant prompts.
6. Credentials belong in environment/secret management. Never print them,
   commit them, or include account responses, cost ledgers, or private queries.
7. Do not change other projects while maintaining this dependency.

Before release, build wheel and sdist, run `scripts/audit_public.py`, install the
wheel in a clean environment, and verify the public API and offline CLI.
