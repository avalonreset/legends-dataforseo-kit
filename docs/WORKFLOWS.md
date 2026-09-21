# Research, save, and resume

These commands work with any agent that can read files and run a terminal.
Use `python -m legends_dataforseo` if the executable is not on PATH.

## Find an unfamiliar operation

```sh
legends-dataforseo docs search "google maps task_post" --limit 3
legends-dataforseo docs read serp/google/maps/task_post
```

Documentation downloads require internet but no API credentials or paid calls.
The next read can use `--offline`. The existing `routes` registry and previews
always work offline, including before any documentation has been cached.
See [documentation discovery](DISCOVERY.md) for cache and source details.

## Save a result once and inspect it repeatedly

Preview first:

```sh
legends-dataforseo serp "coffee" --location-code 2840
```

After reviewing the request and its price, execute with a local ceiling and a
new output filename. The amounts below are example allowances, not price quotes.

```sh
legends-dataforseo serp "coffee" --location-code 2840 --execute --estimated-cost-usd 0.01 --max-cost-usd 0.01 --output coffee-serp.json
legends-dataforseo view coffee-serp.json --select tasks.0.result.0.items --limit 3
legends-dataforseo view coffee-serp.json --summary
```

`--output` saves the complete response and prints a summary with task IDs,
statuses, reported costs, and the file path. An existing output file or missing
parent directory is refused **before HTTP**. Use a new filename for a new call.
If writing fails after the response arrives, the full response is printed to
stdout with an error: preserve it rather than repeating the paid request.
A process interruption may leave a partial file; inspect it and provider task
state before deciding what to do next.

`view` reads local JSON and never calls the provider. `--select` uses dotted keys
and numeric list indexes; repeat it for multiple fields. `--limit` bounds lists
in the displayed view, reports omitted counts, and never truncates the saved
file. Missing selected fields are labelled. Summaries retain **every** task
ID/status even when a displayed data list is limited.

Without output options, request commands still print the original JSON. Python
`api_request` always returns the original response object on envelope success.
CLI transport errors exit 2; a rejected response, if present, produces a task
summary on stdout and can be saved with `--output`. Provider error text is not
copied into the sanitized stderr error.

## Submit a queue once, then retrieve its saved ID

```sh
legends-dataforseo call /serp/google/maps/task_post --body-file examples/maps-tasks.json
```

Review your task JSON and pricing. Add `--execute`, both cost flags, and
`--output submission.json` to submit. Inspect the returned task status and ID.
Replace `SAVED_TASK_ID` with that exact ID:

```sh
legends-dataforseo wait /serp/google/maps/task_get/advanced/SAVED_TASK_ID
legends-dataforseo wait /serp/google/maps/task_get/advanced/SAVED_TASK_ID --execute --attempts 6 --interval 5 --max-elapsed 40 --output retrieval.json
```

The first command previews. The second performs only GET retrievals. It never
submits or resubmits a task. If the result is still pending, run `wait` again
with the same saved ID and a new output filename. A wait output file contains
the report and the last untouched provider envelope under `response`:

```sh
legends-dataforseo view retrieval.json --select response.tasks.0.result.0.items --limit 3
```

Polling continues only for provider statuses `20100`, `40601`, and `40602`.
Success, empty results (`40102`), errors, and unknown/malformed task responses
stop it. Network failures stop immediately. Exit 0 means a report was returned;
inspect `state` and `stop_reason` to distinguish completion from a pending bound.

Defaults: 5 attempts, 5 seconds between attempts, 90-second socket timeout,
300-second elapsed bound. `max_elapsed` prevents further requests and caps their
socket timeout; it is not a hard cancellation deadline for an in-flight response.
`reported_cost_usd` is the last response's reported task cost, not an incremental
retrieval charge. Completed retrievals can repeat the original submission cost:
do not add them together as a bill. Missing cost fields are marked incomplete
instead of being described as free. Reconcile actual billing with the provider.

Supported waits: Google/Bing organic advanced/regular/html, Google Maps advanced,
YouTube organic advanced, and registered free task retrieval routes such as
Google reviews. Other endpoints remain available through reviewed generic calls.

## Optional provider AI responses

The generic transport accepts a terminal `.ai` suffix, for example
`/serp/google/organic/live/advanced.ai`. This is explicit opt-in: standard paths
are never rewritten. Provider AI responses can have a different shape, such as
root-level `id` and `items`, and can omit cost. They are returned unchanged.

Use standard paths plus `--summary`/`--select` when you need ordinary task
envelopes and billing metadata. Existing GeoGrid and GitHub calls keep their
standard paths. `wait` deliberately accepts standard retrieval paths only.

## What a timeout means

The transport never retries. On an ambiguous POST failure,
`ApiError.request_may_have_completed` is true. The CLI includes this flag in its
error JSON. It means the provider may have accepted or charged the request;
it is not permission to submit again. A false flag is not a provider billing
guarantee either. Preserve any `ApiError.response` and inspect task state.

Credentials and result files stay in your environment. The kit never uploads
saved responses, documentation caches, or cost ledgers to GitHub.
