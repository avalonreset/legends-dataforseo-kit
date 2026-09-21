import io
import json
from urllib.error import URLError

import pytest

from legends_dataforseo import documentation as docs


INDEX = """Docs DataForSEO V3
- [Introduction](https://docs.dataforseo.com/v3.md) — Start here
## SERP API
### Google
#### Organic
- [Google Organic live](https://docs.dataforseo.com/v3/serp/google/organic/live/advanced.md) — Search results
- [Google tasks](https://docs.dataforseo.com/v3/serp/google/organic/task_post.md) — Queue searches
## Backlinks API
- [Backlinks summary](https://docs.dataforseo.com/v3/backlinks/summary/live.md) — Link research
- [External](https://example.com/private.md) — Invalid
"""


class Response(io.BytesIO):
    def __init__(self, text, url):
        super().__init__(text.encode() if isinstance(text, str) else text)
        self.url = url

    def geturl(self):
        return self.url


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(docs, "_open", lambda *_: pytest.fail("Unexpected docs network request"))


def serve(monkeypatch, text=INDEX):
    requests = []
    def fetch(request, timeout):
        requests.append(request)
        return Response(text, request.full_url)
    monkeypatch.setattr(docs, "_open", fetch)
    return requests


def test_discovery_search_and_sections(monkeypatch, tmp_path):
    calls = serve(monkeypatch)
    result = docs.docs_index(cache_dir=tmp_path)
    assert len(result["entries"]) == 4
    assert result["entries"][1]["headings"] == ["SERP API", "Google", "Organic"]
    assert result["source_url"] == docs.INDEX_URL
    assert not result["cached"]
    assert docs.docs_sections(cache_dir=tmp_path)["sections"] == ["General", "SERP API", "Backlinks API"]
    assert len(docs.docs_index("serp api", cache_dir=tmp_path)["entries"]) == 2
    search = docs.docs_search("google", limit=1, cache_dir=tmp_path)
    assert search["total_matches"] == 2
    assert len(search["matches"]) == 1
    assert search["cached"]
    assert len(calls) == 1
    assert not calls[0].has_header("Authorization")


def test_offline_cache_allows_stale_and_no_network(monkeypatch, tmp_path):
    serve(monkeypatch)
    docs.docs_index(cache_dir=tmp_path)
    monkeypatch.setattr(docs, "_open", lambda *_: pytest.fail("offline touched network"))
    assert docs.docs_index(cache_dir=tmp_path, offline=True, ttl=0)["stale"]
    with pytest.raises(docs.DocumentationError, match="cached"):
        docs.docs_read("serp/google/locations", cache_dir=tmp_path, offline=True)


def test_expired_refresh_and_corrupt_cache(monkeypatch, tmp_path):
    calls = serve(monkeypatch)
    docs.docs_index(cache_dir=tmp_path)
    docs.docs_index(cache_dir=tmp_path, ttl=0)
    docs.docs_index(cache_dir=tmp_path, refresh=True)
    assert len(calls) == 3
    next(tmp_path.glob("*.json")).write_text("[]")
    with pytest.raises(docs.DocumentationError, match="cached"):
        docs.docs_index(cache_dir=tmp_path, offline=True)
    docs.docs_index(cache_dir=tmp_path)
    assert len(calls) == 4


@pytest.mark.parametrize("path", ["serp/google/locations", "/v3/serp/google/locations/", "https://docs.dataforseo.com/v3/serp/google/locations.md"])
def test_read_normalizes_official_paths(monkeypatch, tmp_path, path):
    calls = serve(monkeypatch, "## Locations\nOfficial reference")
    result = docs.docs_read(path, cache_dir=tmp_path)
    assert result["text"].startswith("## Locations")
    assert calls[0].full_url == "https://docs.dataforseo.com/v3/serp/google/locations.md/"


@pytest.mark.parametrize("path", ["https://evil.com/v3/serp.md", "https://docs.dataforseo.com:443/v3/serp.md", "https://docs.dataforseo.com@evil.com/v3/serp.md", "https://docs.dataforseo.com/private.md", "https://docs.dataforseo.com/v3/serp.md?q=x", "https://docs.dataforseo.com/v3/serp.md#x", "http://docs.dataforseo.com/v3/serp.md", "../secret", "serp/%2e%2e/secret", "serp\\secret", "", None])
def test_unsafe_paths_fail_before_network(tmp_path, path):
    with pytest.raises(docs.DocumentationError):
        docs.docs_read(path, cache_dir=tmp_path)


def test_redirect_handler_refuses_all_redirects():
    with pytest.raises(docs.DocumentationError, match="redirect"):
        docs._NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.com")


def test_final_url_guard(monkeypatch, tmp_path):
    monkeypatch.setattr(docs, "_open", lambda *_: Response("reference", "https://evil.com"))
    with pytest.raises(docs.DocumentationError, match="redirect"):
        docs.docs_index(cache_dir=tmp_path)


@pytest.mark.parametrize("text,expected", [(b"\xff", "decoded"), ("<html>oops", "Markdown"), ("", "Markdown")])
def test_invalid_responses(monkeypatch, tmp_path, text, expected):
    serve(monkeypatch, text)
    with pytest.raises(docs.DocumentationError, match=expected):
        docs.docs_index(cache_dir=tmp_path)


def test_bounded_download(monkeypatch, tmp_path):
    monkeypatch.setattr(docs, "MAX_DOCUMENT_BYTES", 10)
    serve(monkeypatch, "a" * 11)
    with pytest.raises(docs.DocumentationError, match="size limit"):
        docs.docs_index(cache_dir=tmp_path)


def test_network_failure_is_sanitized(monkeypatch, tmp_path):
    def fail(*_):
        raise URLError("secret credential query")
    monkeypatch.setattr(docs, "_open", fail)
    with pytest.raises(docs.DocumentationError) as caught:
        docs.docs_index(cache_dir=tmp_path)
    assert "secret" not in str(caught.value)


@pytest.mark.parametrize("options", [{"timeout": 0}, {"timeout": float("nan")}, {"ttl": -1}, {"ttl": True}, {"offline": "yes"}, {"offline": True, "refresh": True}])
def test_invalid_options(tmp_path, options):
    with pytest.raises(docs.DocumentationError):
        docs.docs_index(cache_dir=tmp_path, **options)


def test_invalid_search_and_index(tmp_path):
    for value in (None, "", " "):
        with pytest.raises(docs.DocumentationError):
            docs.docs_search(value, cache_dir=tmp_path)
    for value in (0, True, 1001):
        with pytest.raises(docs.DocumentationError):
            docs.docs_search("google", limit=value, cache_dir=tmp_path)


def test_poisoned_cache_url_is_ignored(monkeypatch, tmp_path):
    serve(monkeypatch)
    docs.docs_index(cache_dir=tmp_path)
    target = next(tmp_path.glob("*.json"))
    data = json.loads(target.read_text())
    data["source_url"] = "https://evil.com"
    target.write_text(json.dumps(data))
    with pytest.raises(docs.DocumentationError, match="cached"):
        docs.docs_index(cache_dir=tmp_path, offline=True)


def test_read_only_cache_preserves_download(monkeypatch, tmp_path):
    serve(monkeypatch, "# Official reference")
    cache_file = tmp_path / "file-not-directory"
    cache_file.write_text("existing user data")
    result = docs.docs_read("auth", cache_dir=cache_file)
    assert result["text"] == "# Official reference"
    assert "cache_warning" in result
    assert cache_file.read_text() == "existing user data"


def test_malformed_index_fails_clearly(monkeypatch, tmp_path):
    serve(monkeypatch, "No Markdown references here")
    with pytest.raises(docs.DocumentationError, match="no recognized entries"):
        docs.docs_index(cache_dir=tmp_path)


def test_stale_cache_is_not_silently_used_on_network_failure(monkeypatch, tmp_path):
    serve(monkeypatch)
    docs.docs_index(cache_dir=tmp_path)
    def fail(*_):
        raise URLError("unavailable")
    monkeypatch.setattr(docs, "_open", fail)
    with pytest.raises(docs.DocumentationError, match="downloaded"):
        docs.docs_index(cache_dir=tmp_path, ttl=0)
    assert docs.docs_index(cache_dir=tmp_path, offline=True, ttl=0)["stale"]
