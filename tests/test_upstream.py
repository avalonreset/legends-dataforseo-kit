import importlib.util
import io
import json
from pathlib import Path
from urllib.error import URLError

import pytest


spec = importlib.util.spec_from_file_location("check_upstream", Path(__file__).resolve().parents[1] / "scripts" / "check_upstream.py")
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)


class Response(io.BytesIO):
    def geturl(self):
        return upstream.SOURCE_URL


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(upstream, "_open", lambda *_: pytest.fail("Unexpected upstream network request"))


def serve(monkeypatch, data):
    def fetch(request, timeout):
        assert not request.has_header("Authorization")
        assert timeout == 20
        return Response(json.dumps(data).encode())
    monkeypatch.setattr(upstream, "_open", fetch)


@pytest.mark.parametrize("version,commit,changed", [("3.1.1", upstream.BASELINE_COMMIT, False), ("3.1.2", "newcommit", True), ("3.1.1", None, True)])
def test_baseline_detection(monkeypatch, version, commit, changed):
    serve(monkeypatch, {"name": "dataforseo-mcp-server", "version": version, "gitHead": commit})
    result = upstream.check_upstream()
    assert result["changed"] is changed
    assert result["baseline"]["git_head"] == upstream.BASELINE_COMMIT


@pytest.mark.parametrize("data", [[], {}, {"name": "other"}, {"name": "dataforseo-mcp-server", "version": 123}])
def test_invalid_metadata(monkeypatch, data):
    serve(monkeypatch, data)
    with pytest.raises(upstream.UpstreamError):
        upstream.check_upstream()


def test_sanitized_failure(monkeypatch, capsys):
    def fail(*_):
        raise URLError("private proxy credential")
    monkeypatch.setattr(upstream, "_open", fail)
    assert upstream.main() == 2
    assert "private" not in capsys.readouterr().out


def test_size_limit(monkeypatch):
    serve(monkeypatch, {"name": "dataforseo-mcp-server", "version": "3.1.1"})
    monkeypatch.setattr(upstream, "MAX_BYTES", 5)
    with pytest.raises(upstream.UpstreamError, match="size limit"):
        upstream.check_upstream()


def test_redirect_refused():
    with pytest.raises(upstream.UpstreamError, match="redirect"):
        upstream._NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com")
