# CLI guide

Run `legends-dataforseo --help` or `python -m legends_dataforseo --help`.
Output is JSON. Successful commands exit `0`; input, credential, or transport
errors exit `2` and write a sanitized error to stderr. Returned per-task errors
remain in the provider envelope; inspect them even when the command exits `0`.

## Offline commands

```sh
legends-dataforseo doctor
legends-dataforseo routes
legends-dataforseo route maps-task-post
legends-dataforseo estimate maps --tasks 9 --depth 100
legends-dataforseo serp "technical SEO" --location-code 2840
legends-dataforseo demand "technical SEO" "local SEO"
legends-dataforseo maps "coffee" --location-coordinate "40.7128,-74.0060,15z"
```

Named request commands preview by default. The registry includes endpoint
descriptions beyond the three named helpers; discovery is not a promise that
every route has its own command or has been live-tested.

## Generic endpoints and queues

Preview the included synthetic task file from a source checkout:

```sh
legends-dataforseo call /serp/google/maps/task_post --body-file examples/maps-tasks.json
```

For your own request, supply a UTF-8 JSON array of task objects. Do not put
credentials in it. A body selects POST; no body selects GET. `--method` can make
that choice explicit. Only documented relative DataForSEO v3 paths are accepted.

After approval, add `--execute --estimated-cost-usd <ESTIMATE> --max-cost-usd <CEILING>`
with real reviewed amounts. For a known saved task, replace `<TASK_ID>` below:

```text
legends-dataforseo call /serp/google/maps/task_get/advanced/<TASK_ID> --execute
```

The CLI still needs `--execute` to send a retrieval request. Registered task
retrieval GETs do not require paid cost flags. Keep the returned task ID and
status; polling and retry decisions belong to the caller.

## Execution options

| Option | Meaning |
| --- | --- |
| `--execute` | Send this request; absent means preview. |
| `--estimated-cost-usd` | Reviewed estimate for the entire request. Required for paid POST execution. |
| `--max-cost-usd` | Local estimate ceiling, not a provider billing cap. Required for paid POST execution. |
| `--timeout` | Request timeout in seconds; default 90. |
| `--language-code` | Named-helper language code; default `en`. |
| `--location-code` | SERP/demand location code; default `2840`. |
| `--location-coordinate` | Required Maps coordinate and zoom value. |
| `--depth` | SERP/Maps result depth; defaults 10/100 respectively. |

Each subcommand's `--help` lists the options it accepts. Baseline estimates can
become outdated. Standard queue pricing needs a separately reviewed estimate.

[First live request](FIRST-USE.md) · [Credential setup](INSTALL.md#credentials) · [Python API](API.md)
