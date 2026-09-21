"""JSON CLI with offline previews and explicit execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .client import (ApiError, CredentialError, RouteError, api_request,
                     credential_status, estimate_cost, load_routes, route_for)


def _execution_flags(parser):
    parser.add_argument("--execute", action="store_true", help="Confirm this request may incur charges")
    parser.add_argument("--estimated-cost-usd", type=float, help="Reviewed estimate for this entire request")
    parser.add_argument("--max-cost-usd", type=float, help="Local preflight ceiling; not a provider billing cap")
    parser.add_argument("--timeout", type=float, default=90)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="legends-dataforseo", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("routes", help="Offline operation registry")
    route = sub.add_parser("route")
    route.add_argument("operation")
    estimate = sub.add_parser("estimate", help="Offline baseline estimate")
    estimate.add_argument("operation")
    estimate.add_argument("--tasks", type=int, default=1)
    estimate.add_argument("--depth", type=int, default=0)
    estimate.add_argument("--items", type=int, default=0)
    doctor = sub.add_parser("doctor", help="Installation and credential presence; no values")
    doctor.add_argument("--live", action="store_true", help="Also make a no-charge account authentication probe")
    call = sub.add_parser("call", help="Preview or execute a documented v3 endpoint")
    call.add_argument("path")
    call.add_argument("--method", choices=["GET", "POST"], default=None)
    call.add_argument("--body-file", type=Path, help="UTF-8 JSON task array; do not include credentials")
    _execution_flags(call)
    for name in ("serp", "maps", "demand"):
        command = sub.add_parser(name, help="Preview a " + name + " task; --execute sends it")
        command.add_argument("keywords", nargs="+" if name == "demand" else 1)
        command.add_argument("--language-code", default="en")
        if name == "maps":
            command.add_argument("--location-coordinate", required=True)
        else:
            command.add_argument("--location-code", type=int, default=2840)
        if name != "demand":
            command.add_argument("--depth", type=int, default=100 if name == "maps" else 10)
        _execution_flags(command)
    args = parser.parse_args(argv)
    try:
        if args.command == "routes":
            result = load_routes()
        elif args.command == "route":
            result = route_for(args.operation)
        elif args.command == "estimate":
            result = estimate_cost(args.operation, tasks=args.tasks, depth=args.depth, items=args.items)
        elif args.command == "doctor":
            result = {"version": __version__, "routes": len(load_routes()["routes"]),
                      "credentials": credential_status(), "live": False}
            if args.live:
                response = api_request("/appendix/user_data")
                statuses = [t.get("status_code") for t in response.get("tasks") or []]
                if not statuses or any(s != 20000 for s in statuses):
                    raise ApiError("Live authentication probe did not succeed.")
                result.update(live=True, status_code=response["status_code"], cost=response.get("cost"))
        else:
            if args.command == "call":
                path = args.path
                payload = json.loads(args.body_file.read_text(encoding="utf-8-sig")) if args.body_file else None
                method = args.method or ("POST" if payload is not None else "GET")
            else:
                path = route_for(args.command)["path"]
                task = {"language_code": args.language_code}
                if args.command == "demand":
                    task.update(keywords=args.keywords, location_code=args.location_code)
                else:
                    task.update(keyword=args.keywords[0], depth=args.depth)
                    if args.command == "maps":
                        task["location_coordinate"] = args.location_coordinate
                    else:
                        task["location_code"] = args.location_code
                payload, method = [task], "POST"
            if not args.execute:
                result = {"preview": True, "path": path, "method": method, "body": payload,
                          "estimated_cost_usd": args.estimated_cost_usd, "max_cost_usd": args.max_cost_usd}
            else:
                if method == "POST" and (args.estimated_cost_usd is None or args.max_cost_usd is None):
                    raise RouteError("Paid CLI execution requires --estimated-cost-usd and --max-cost-usd.")
                result = api_request(path, payload, method=method, confirm=True, timeout=args.timeout,
                                     consumer="cli", estimated_cost_usd=args.estimated_cost_usd,
                                     max_cost_usd=args.max_cost_usd)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ApiError, CredentialError, RouteError, ValueError, OSError) as exc:
        # Provider response bodies and OS error details may contain private input.
        message = str(exc) if isinstance(exc, (ApiError, CredentialError, RouteError)) else "Invalid input or local file error."
        print(json.dumps({"error": type(exc).__name__, "message": message}), file=sys.stderr)
        return 2
