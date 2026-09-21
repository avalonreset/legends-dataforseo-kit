# Python contract — 0.3.x

Public import: `legends_dataforseo`. Package: `legends-dataforseo-kit`.
`API_ROOT = "https://api.dataforseo.com/v3"`.

```python
api_request(
    path, payload=None, *, method=None, body=None,
    credentials=None, timeout=90, log_cost=False, confirm=False,
    consumer="python", estimated_cost_usd=None, max_cost_usd=None,
) -> dict

serp(keyword, *, location_code=2840, language_code="en", depth=10,
     **request_options) -> dict
demand(keywords, *, location_code=2840, language_code="en",
       **request_options) -> dict
maps(keyword, *, location_coordinate, language_code="en", depth=100,
     **request_options) -> dict
```

`payload` is the existing positional task array. `body` is its keyword alias;
specify only one. `method` is GET or POST; if omitted, a payload selects POST,
otherwise GET. POST requires a nonempty list of task objects. A live SERP call
accepts exactly one task; a SERP queue POST accepts at most 100. Use raw
`api_request` for endpoint-specific fields not exposed by the named helpers.

`path` is relative to v3, optionally beginning `/v3/`. Absolute URLs, query
strings, encoded path traversal, and redirects are rejected. No alternate host
option exists. TLS verification remains enabled.

`confirm=True` is a noninteractive paid/raw opt-in. It is mandatory for POST
and unclassified GET requests. Registered free GET and task retrieval GET need
no paid opt-in. A caller that already approved a scan passes confirm on its
paid request; the transport never adds another approval dialog.

`estimated_cost_usd` is the caller's reviewed estimate for the whole request.
When `max_cost_usd` is supplied, an estimate is required and must not exceed the
ceiling. Both must be finite, nonnegative numbers. This rejects requests before
credentials or HTTP; it is not a provider-side spending limit, reservation,
multi-request budget, or guaranteed price. The caller owns those policies.

## Responses and errors

Returns the complete JSON object when the top-level status is `20000`.
Per-task statuses are never converted into transport errors, even when
`tasks_error` is nonzero. This preserves `20100`, `40601`, `40602`, `40102`, and
other statuses so the caller can distinguish pending, empty, and failed tasks.

`ApiError` indicates an HTTP, network, decoding, or top-level envelope failure.
It has `.response` (decoded object or None) and `.http_status` (integer or None).
Exception messages do not echo provider text, query bodies, or credentials.
Treat `.response` as private data. `CredentialError` means missing/incomplete
credentials; `RouteError` is invalid input; `CostLimitError(ApiError)` is a
preflight refusal. There are no automatic retries, account fallbacks, queue
polls, or sleeps. A timeout does not prove that the provider did not charge.

```python
from legends_dataforseo import ApiError, api_request

try:
    response = api_request("/serp/google/maps/task_get/advanced/" + task_id)
except ApiError as error:
    response = error.response  # Keep private; classify before another request.
```

## Credentials and local state

`Credentials(login, password, source="explicit")` hides login/password in repr.
Explicit credentials override the environment. Otherwise `load_credentials()`
uses DATAFORSEO_LOGIN or DATAFORSEO_USERNAME plus DATAFORSEO_PASSWORD. A partial
process pair fails rather than falling through to another account. Windows
user-scope fallback applies only when the process pair is entirely absent.

No account identity, legacy credentials, account-routing state, or credential
files are bundled. `credential_status()` returns presence/source only.
`log_cost=False` is the default. Opt-in cost logging uses
`LEGENDS_DATAFORSEO_LEDGER` or a user state directory (LOCALAPPDATA,
XDG_STATE_HOME, or ~/.local/state). It stores timestamp, endpoint template,
cost, top-level status, and caller-supplied consumer label. Use a non-sensitive
consumer label. Ledger errors warn without hiding the completed API response.

Offline helpers: `load_routes()`, `route_for(operation)`,
`estimate_cost(operation, *, tasks=1, depth=0, items=0)`, `total_cost(responses)`.
`write_json(Path, payload)` explicitly saves caller-selected data.

## Compatibility

0.3.0 is the first public release, following private local prototypes. It keeps
the positional `api_request(path, payload)` transport and timeout/consumer/confirm
keywords. Public defaults are single-account, all paid calls confirmed, logging
off, and task statuses caller-owned. Private account failover, workstation
installers, and PowerShell-specific wrappers are not part of the public API.
Pin a release or full commit. Breaking changes will be documented and versioned.
