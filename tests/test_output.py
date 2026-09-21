import copy
import json

import pytest

from legends_dataforseo import ApiError, cli, response_view
from legends_dataforseo.output import ResponseFile, validate_view


@pytest.fixture
def envelope():
    return {"status_code": 20000, "cost": 0.002, "tasks_count": 2, "tasks_error": 1,
            "tasks": [{"id": "saved-one", "status_code": 20000, "cost": 0.002,
                       "data": {"keyword": "private-query"},
                       "result": [{"items": [{"title": str(i)} for i in range(10)]}]},
                      {"id": "saved-two", "status_code": 40102, "result": None}]}


def test_default_is_equal_independent_copy(envelope):
    view = response_view(envelope)
    assert view == envelope and view is not envelope
    view["tasks"][0]["id"] = "changed"
    assert envelope["tasks"][0]["id"] == "saved-one"


def test_projection_retains_all_statuses_and_counts_omissions(envelope):
    original = copy.deepcopy(envelope)
    path = "tasks.0.result.0.items"
    result = response_view(envelope, select=[path, "tasks.2.result"], limit=2)
    assert len(result["selected"][path]) == 2
    assert result["omitted_items"][path] == 8
    assert result["missing_fields"] == ["tasks.2.result"]
    assert [task["id"] for task in result["summary"]["tasks"]] == ["saved-one", "saved-two"]
    assert result["summary"]["tasks"][1]["status_code"] == 40102
    assert "private-query" not in json.dumps(result)
    assert envelope == original


def test_summary_excludes_results_and_private_request(envelope):
    result = response_view(envelope, summary=True)
    assert result["summary"]["tasks"][0]["items_returned"] == 10
    assert "private-query" not in json.dumps(result)
    assert "selected" not in result


def test_ai_summary_retains_root_task_id_and_marks_missing_cost():
    result = response_view({"id": "ai-task", "status_code": 20000, "items": [{"title": "a"}]}, summary=True)
    assert result["summary"] == {"id": "ai-task", "status_code": 20000, "items_returned": 1, "cost_reported": False}


@pytest.mark.parametrize("select,limit", [(["../oops"], None), (["a.*"], None), ([""], None),
                                         (["1" * 5000], None), (None, 0), (None, -1), (None, True)])
def test_invalid_views_rejected(select, limit):
    with pytest.raises(ValueError):
        validate_view(select, limit)


def test_save_preserves_full_response_and_prints_only_summary(tmp_path, monkeypatch, capsys, envelope):
    target = tmp_path / "result.json"
    monkeypatch.setattr(cli, "api_request", lambda *a, **kw: envelope)
    assert cli.main(["call", "/appendix/status", "--execute", "--output", str(target)]) == 0
    assert json.loads(target.read_text()) == envelope
    displayed = json.loads(capsys.readouterr().out)
    assert displayed["output_file"] == str(target)
    assert "private-query" not in json.dumps(displayed)


def test_existing_output_refused_before_http(tmp_path, monkeypatch, capsys):
    target = tmp_path / "existing.json"
    target.write_text("keep")
    monkeypatch.setattr(cli, "api_request", lambda *a, **kw: pytest.fail("must not call HTTP"))
    assert cli.main(["call", "/appendix/status", "--execute", "--output", str(target)]) == 2
    assert target.read_text() == "keep"
    assert "FileExistsError" in capsys.readouterr().err


def test_invalid_select_refused_before_http(monkeypatch, capsys):
    monkeypatch.setattr(cli, "api_request", lambda *a, **kw: pytest.fail("must not call HTTP"))
    assert cli.main(["call", "/appendix/status", "--execute", "--select", "a.*"]) == 2
    assert capsys.readouterr().out == ""


def test_save_failure_keeps_received_response_on_stdout(tmp_path, monkeypatch, capsys, envelope):
    monkeypatch.setattr(cli, "api_request", lambda *a, **kw: envelope)
    def disk_failure(*args):
        raise OSError("private-path")
    monkeypatch.setattr(ResponseFile, "write", disk_failure)
    assert cli.main(["call", "/appendix/status", "--execute", "--output", str(tmp_path / "out.json")]) == 2
    captured = capsys.readouterr()
    assert json.loads(captured.out) == envelope
    assert "do not repeat" in captured.err and "private-path" not in captured.err


def test_rejected_envelope_saved_without_exposing_provider_error(tmp_path, monkeypatch, capsys):
    rejected = {"status_code": 40501, "status_message": "private-provider-message", "tasks": []}
    def fail(*a, **kw):
        raise ApiError("Rejected envelope", response=rejected)
    monkeypatch.setattr(cli, "api_request", fail)
    target = tmp_path / "rejected.json"
    assert cli.main(["call", "/appendix/status", "--execute", "--output", str(target)]) == 2
    captured = capsys.readouterr()
    assert json.loads(target.read_text()) == rejected
    assert "private-provider-message" not in captured.out + captured.err


def test_offline_saved_view_never_calls_api(tmp_path, monkeypatch, capsys, envelope):
    target = tmp_path / "saved.json"
    target.write_text(json.dumps(envelope))
    assert cli.main(["view", str(target), "--select", "tasks.0.result.0.items", "--limit", "1"]) == 0
    assert len(json.loads(capsys.readouterr().out)["selected"]["tasks.0.result.0.items"]) == 1


def test_wait_preview_never_calls_api(capsys):
    assert cli.main(["wait", "/serp/google/maps/task_get/advanced/saved-id"]) == 0
    assert json.loads(capsys.readouterr().out)["preview"] is True


def test_wait_cli_calls_only_saved_get_and_preserves_bounds(monkeypatch, capsys):
    calls = []
    from legends_dataforseo import client
    def respond(path, **kwargs):
        calls.append((path, kwargs))
        return {"status_code": 20000, "cost": 0, "tasks": [{"id": "saved-id", "status_code": 40601}]}
    monkeypatch.setattr(client, "api_request", respond)
    assert cli.main(["wait", "/serp/google/maps/task_get/advanced/saved-id", "--execute",
                     "--attempts", "2", "--interval", "0", "--summary"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert len(calls) == 2 and all(options["method"] == "GET" for _, options in calls)
    assert output["summary"]["state"] == "pending"
    assert output["summary"]["response"]["tasks"][0]["id"] == "saved-id"
