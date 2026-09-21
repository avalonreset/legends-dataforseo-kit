from contextlib import contextmanager
from http.client import IncompleteRead, RemoteDisconnected
import json
import warnings

import pytest

from legends_dataforseo import ApiError, Credentials, CostLimitError, RouteError, __version__, client, cli


CREDS = Credentials("test-login", "test-password")


@contextmanager
def response(value):
    from io import BytesIO
    yield BytesIO(json.dumps(value).encode())


@pytest.mark.parametrize("failure", [IncompleteRead(b"private body", 10), RemoteDisconnected("private-details")])
def test_protocol_failure_is_sanitized_and_never_retried(monkeypatch, failure):
    calls = []
    def broken(*args):
        calls.append(args)
        raise failure
    monkeypatch.setattr(client, "_open", broken)
    with pytest.raises(ApiError) as error:
        client.api_request("/serp/google/organic/live/advanced", [{}], credentials=CREDS, confirm=True)
    assert len(calls) == 1
    assert error.value.request_may_have_completed is True
    assert "private" not in str(error.value)


def test_warning_as_error_cannot_hide_received_response(monkeypatch):
    raw = {"status_code": 20000, "cost": 0.002, "tasks": [{"id": "saved-id", "status_code": 20100}]}
    monkeypatch.setattr(client, "_open", lambda *_: response(raw))
    def failure(*args):
        raise OSError("private-path")
    monkeypatch.setattr(client, "_append_ledger", failure)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert client.api_request("/serp/google/maps/task_post", [{}], credentials=CREDS,
                                  confirm=True, log_cost=True) == raw


def test_rejected_cli_response_retains_ids_without_file(monkeypatch, capsys):
    def rejected(*args, **kwargs):
        raise ApiError("Rejected", response={"status_code": 50000, "status_message": "private-body",
                       "tasks": [{"id": "keep-this-id", "status_code": 20100}]})
    monkeypatch.setattr(cli, "api_request", rejected)
    assert cli.main(["call", "/appendix/status", "--execute"]) == 2
    output = capsys.readouterr()
    assert json.loads(output.out)["summary"]["tasks"][0]["id"] == "keep-this-id"
    assert "private-body" not in output.out + output.err


def test_ai_path_preserves_original_envelope_and_dynamic_user_agent(monkeypatch):
    raw = {"status_code": 20000, "tasks": [{"status_code": 40102, "result": None}]}
    calls = []
    def opened(request, timeout):
        calls.append(request)
        return response(raw)
    monkeypatch.setattr(client, "_open", opened)
    assert client.api_request("/v3/serp/google/organic/live/advanced.ai", [{}], credentials=CREDS, confirm=True) == raw
    assert calls[0].full_url.endswith("advanced.ai")
    assert calls[0].get_header("User-agent") == "legends-dataforseo-kit/" + __version__


def test_ai_paths_cannot_bypass_cost_and_task_count_guards():
    with pytest.raises(CostLimitError):
        client.api_request("/serp/google/organic/live/advanced.ai", [{}])
    with pytest.raises(RouteError):
        client.api_request("/serp/google/maps/task_post.ai", [{}] * 101, confirm=True)
    with pytest.raises(RouteError):
        client.api_request("/serp/google/organic/live/advanced.ai", [{}, {}], confirm=True)


@pytest.mark.parametrize("path", ["/serp/../secrets.ai", "/serp/path.ai.ai", "/serp/path.ai/child", "/serp/path?x=.ai"])
def test_only_terminal_ai_suffix_allowed(path):
    with pytest.raises(RouteError):
        client.normalize_path(path)
