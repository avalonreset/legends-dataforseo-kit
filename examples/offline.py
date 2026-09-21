"""Credential-free discovery and synthetic queued/empty result handling."""

import json

from legends_dataforseo import estimate_cost, route_for

fixture = {"status_code": 20000, "cost": 0, "tasks": [
    {"id": "synthetic-pending", "status_code": 40601, "result": None},
    {"id": "synthetic-empty", "status_code": 40102, "result": [{"items": None}]},
]}
print(json.dumps({"route": route_for("maps-task-post")["path"],
                  "estimate": estimate_cost("maps", tasks=9, depth=100),
                  "synthetic_statuses": [task["status_code"] for task in fixture["tasks"]]}, indent=2))
