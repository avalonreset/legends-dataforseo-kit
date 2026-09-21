"""Read-only npm baseline check. Does not install or execute upstream code."""
from datetime import datetime, timezone
from http.client import HTTPException
import json
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASELINE_VERSION = "3.1.1"
BASELINE_COMMIT = "fde5554e7b57f40528e73e55d90c82c8300b726b"
SOURCE_URL = "https://registry.npmjs.org/dataforseo-mcp-server/latest"
MAX_BYTES = 1024 * 1024


class UpstreamError(ValueError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise UpstreamError("Upstream metadata redirects are not permitted")


def _open(request, timeout):
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


def check_upstream():
    request = Request(SOURCE_URL, headers={"Accept": "application/json", "User-Agent": "legends-dataforseo-kit upstream-check"})
    try:
        with _open(request, 20) as response:
            if response.geturl() != SOURCE_URL:
                raise UpstreamError("Upstream metadata redirects are not permitted")
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise UpstreamError("Upstream metadata exceeds the size limit")
        metadata = json.loads(raw)
    except (URLError, OSError, HTTPException, UnicodeError, json.JSONDecodeError):
        raise UpstreamError("Could not retrieve valid upstream package metadata") from None
    if not isinstance(metadata, dict) or metadata.get("name") != "dataforseo-mcp-server":
        raise UpstreamError("Unexpected upstream package metadata")
    version, commit = metadata.get("version"), metadata.get("gitHead")
    if not isinstance(version, str) or not version or (commit is not None and not isinstance(commit, str)):
        raise UpstreamError("Upstream version metadata is missing or invalid")
    return {
        "package": "dataforseo-mcp-server", "source_url": SOURCE_URL,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "baseline": {"version": BASELINE_VERSION, "git_head": BASELINE_COMMIT},
        "observed": {"version": version, "git_head": commit},
        "changed": version != BASELINE_VERSION or commit != BASELINE_COMMIT,
        "review_required": version != BASELINE_VERSION or commit != BASELINE_COMMIT,
    }


def main():
    try:
        print(json.dumps(check_upstream(), indent=2))
        return 0
    except UpstreamError as error:
        print(json.dumps({"error": "UpstreamError", "message": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
