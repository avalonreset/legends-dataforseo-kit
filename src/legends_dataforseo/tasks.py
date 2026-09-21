"""Opt-in, bounded retrieval of one previously submitted task.

No submissions, retries after transport failures, or hidden persistence. Status
meanings: https://docs.dataforseo.com/v3/appendix-errors/
"""

from __future__ import annotations

import math
import re
import time
from typing import Any

from . import client

PENDING_STATUSES = frozenset({20100, 40601, 40602})
# Deliberately finite: adding a retrieval endpoint requires reviewing its docs.
_SERP_RETRIEVAL = re.compile(
    r"/serp/(?:(?:google|bing)/organic/task_get/(?:advanced|regular|html)"
    r"|google/maps/task_get/advanced|youtube/organic/task_get/advanced)/[A-Za-z0-9_-]+"
)


def retrieval_path(path: str) -> str:
    """Validate a known retrieval path before credentials or any HTTP access."""
    normalized = client.normalize_path(path)
    if _SERP_RETRIEVAL.fullmatch(normalized):
        return normalized
    for route in client.load_routes()["routes"]:
        template = route["path"]
        if (route["method"] == "GET" and not route["charged"]
                and "/task_get/" in template and template.endswith("/{id}")):
            pattern = re.escape(template[:-4]) + r"[A-Za-z0-9_-]+"
            if re.fullmatch(pattern, normalized):
                return normalized
    raise client.RouteError("wait_task requires a supported task_get path with a saved task ID.")


def _number(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(name + " must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(name + " must be a finite number") from None
    if not math.isfinite(number) or number < 0 or (positive and number == 0):
        raise ValueError(name + " must be finite and " + ("positive" if positive else "nonnegative"))
    return number


def _state(response: dict[str, Any]) -> str:
    tasks = response.get("tasks")
    # One saved ID should return one task. Never keep polling malformed output.
    if not isinstance(tasks, list) or len(tasks) != 1 or not isinstance(tasks[0], dict):
        return "stopped"
    code = tasks[0].get("status_code")
    if type(code) is not int:
        return "stopped"
    if code in PENDING_STATUSES:
        return "pending"
    if code == 20000:
        return "completed"
    if code == 40102:
        return "empty"
    return "stopped"


def wait_task(
    path: str, *, max_attempts: int = 5, interval: float = 5,
    timeout: float = 90, max_elapsed: float = 300,
    credentials: client.Credentials | None = None,
    consumer: str = "python", log_cost: bool = False,
) -> dict[str, Any]:
    """Retrieve a saved task until terminal status or an explicit local bound.

    Only 20100 (created), 40601 (handed), and 40602 (queued) are polled.
    Unknown, failed, empty, or malformed task statuses stop immediately. The
    original last envelope is returned as ``response``; transport errors
    propagate unchanged, including ``ApiError.response``, without another call.

    ``max_elapsed`` prevents starting requests after the elapsed bound and caps
    their socket timeout to the remaining time. It is not a hard wall-clock
    cancellation deadline: urllib's timeout is a socket-operation timeout.
    Reported cost is only the last response's provider-reported task cost. It
    may repeat the original submission charge; it is not incremental billing,
    a sum across polls, or a spending cap. Missing/invalid cost returns None.
    No task IDs or responses are saved automatically.
    """
    normalized = retrieval_path(path)
    if type(max_attempts) is not int or not 1 <= max_attempts <= 1000:
        raise ValueError("max_attempts must be an integer between 1 and 1000")
    interval = _number(interval, "interval")
    timeout = _number(timeout, "timeout", positive=True)
    max_elapsed = _number(max_elapsed, "max_elapsed", positive=True)
    started = time.monotonic()
    attempts = 0
    response = None
    state = "pending"
    cost = None
    cost_complete = False
    reason = "max_attempts"
    while attempts < max_attempts:
        remaining = max_elapsed - (time.monotonic() - started)
        if remaining <= 0:
            reason = "max_elapsed"
            break
        response = client.api_request(
            normalized, method="GET", timeout=min(timeout, remaining),
            credentials=credentials, consumer=consumer, log_cost=log_cost,
        )
        attempts += 1
        reported = response.get("cost")
        try:
            cost = _number(reported, "reported cost")
            cost_complete = True
        except ValueError:
            cost = None
            cost_complete = False
        state = _state(response)
        if state != "pending":
            reason = "terminal_status" if state != "stopped" else "unrecognized_or_failed_status"
            break
        if attempts == max_attempts:
            break
        remaining = max_elapsed - (time.monotonic() - started)
        if remaining <= 0:
            reason = "max_elapsed"
            break
        time.sleep(min(interval, remaining))
    return {
        "state": state, "stop_reason": reason, "attempts": attempts,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "reported_cost_usd": cost, "reported_cost_complete": cost_complete,
        "cost_scope": "last_response_not_incremental_billing",
        "response": response,
    }
