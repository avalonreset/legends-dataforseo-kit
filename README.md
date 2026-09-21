# legends-dataforseo-kit

An early open-source Python package and CLI for DataForSEO API v3. Use it from
scripts, applications, or any coding agent. No MCP server or agent-specific
runtime is required. Python 3.10+; Windows, Linux, and macOS; no runtime dependencies.

Supports Google SERP, Maps live and queued tasks, keyword demand, and documented
v3 endpoints. Returns provider JSON without discarding queued, empty, or failed
task statuses. Includes offline discovery, estimates, and examples.

## Install

```sh
python -m pip install "git+https://github.com/avalonreset/legends-dataforseo-kit.git@v0.3.0"
legends-dataforseo --version
legends-dataforseo doctor
```

The Git install requires Git. A wheel is available on the
[v0.3.0 release](https://github.com/avalonreset/legends-dataforseo-kit/releases/tag/v0.3.0):

```sh
python -m pip install "https://github.com/avalonreset/legends-dataforseo-kit/releases/download/v0.3.0/legends_dataforseo_kit-0.3.0-py3-none-any.whl"
```

There is no PyPI publication for this release. Dependency managers can pin the
full commit listed in the release for reproducible source installs.

## Start offline

```sh
legends-dataforseo routes
legends-dataforseo estimate maps --tasks 9 --depth 100
legends-dataforseo serp "technical SEO" --location-code 2840
legends-dataforseo demand "technical SEO" "local SEO"
```

Named commands preview by default. These commands make no network requests and
need no credentials. Baseline estimates are advisory and can become outdated.
Queue pricing requires a separately reviewed estimate.

## Configure credentials

Set `DATAFORSEO_LOGIN` (or `DATAFORSEO_USERNAME`) and `DATAFORSEO_PASSWORD` using
your shell or secret manager. The loader reads a complete process environment
pair first, then the Windows user environment. It never mixes scopes, reads a
credential file, or prompts. Do not put credentials in source or command arguments.

`legends-dataforseo doctor --live` verifies authentication with a no-charge
request and prints only status, cost, and credential presence.

## Python API

```python
from legends_dataforseo import api_request

# This sends a paid request. Set confirm only after reviewing the scan budget.
response = api_request(
    "/serp/google/maps/task_post",
    [{"keyword": "coffee", "location_coordinate": "40.7128,-74.0060,15z",
      "language_code": "en", "depth": 100, "priority": 1}],
    confirm=True,
    consumer="my-app",
    estimated_cost_usd=0.01,  # Example reviewed allowance; not a price quote.
    max_cost_usd=0.01,
)
for task in response.get("tasks") or []:
    # Save task IDs; inspect status before polling. Never blindly resubmit.
    print(task.get("id"), task.get("status_code"))
```

Retrieve a saved task with
`api_request("/serp/google/maps/task_get/advanced/" + task_id)`. The caller controls
polling, interprets all task statuses, and owns the aggregate scan budget.
`40102` means an empty search result, not proof of no market demand.

`serp(keyword, ...)`, `demand(keywords, ...)`, and `maps(keyword, ...)` convenience
functions also accept `confirm`, `estimated_cost_usd`, `max_cost_usd`, and `timeout`.
See the [versioned API contract](docs/API.md) for signatures and error handling.

## Cost and privacy

Paid or unclassified requests require `confirm=True` in Python. Paid CLI calls
require `--execute`, `--estimated-cost-usd`, and `--max-cost-usd`. No interactive
prompt is repeated after these explicit options. The ceiling compares your
estimate before HTTP; it cannot enforce provider billing. Review
[current pricing](https://dataforseo.com/pricing) and reconcile `response.cost`.

Requests are never retried or switched between accounts. Responses remain in
memory unless the caller saves them. Optional `log_cost=True` writes only cost
metadata to a user state directory. Provider responses can contain private
queries or account information; do not publish them.

## Development and agent use

```sh
python -m pip install -e ".[dev]"
python -m pytest
python examples/offline.py
python -m build
python -m twine check dist/*
```

CI tests Linux, Windows, and macOS without credentials or paid calls. Read
[AGENTS.md](AGENTS.md) or [the portable skill](skills/legends-dataforseo-kit/SKILL.md)
for agent-assisted install and operation. Consumer integration recipes for
legends-geogrid and legends-github are in [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md).

MIT licensed. [Provenance](docs/PROVENANCE.md). Independent project; not an
official DataForSEO SDK. The license covers this code, not the provider service,
data, or trademarks.
