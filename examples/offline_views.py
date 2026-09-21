"""Run without credentials: complete envelopes and compact views coexist."""
import json

from legends_dataforseo import response_view

# Synthetic data only. Real responses may contain private queries and results.
raw = {"status_code": 20000, "cost": 0, "tasks": [
    {"id": "synthetic-task", "status_code": 20000, "result": [
        {"items": [{"title": "Example " + str(i), "rank_absolute": i} for i in range(1, 11)]}
    ]}
]}
view = response_view(raw, select=["tasks.0.result.0.items"], limit=2)
assert len(raw["tasks"][0]["result"][0]["items"]) == 10
assert view["omitted_items"]["tasks.0.result.0.items"] == 8
assert view["summary"]["tasks"][0]["id"] == "synthetic-task"
print(json.dumps(view, indent=2))
