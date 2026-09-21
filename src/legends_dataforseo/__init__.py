"""Public, agent-neutral DataForSEO API v3 transport."""

__version__ = "0.3.0"

from .client import (
    API_ROOT, ApiError, CostLimitError, CredentialError, Credentials, RouteError,
    api_request, credential_status, demand, estimate_cost, ledger_path,
    load_credentials, load_routes, maps, route_for, serp, total_cost, write_json,
)

__all__ = [
    "API_ROOT", "ApiError", "CostLimitError", "CredentialError", "Credentials",
    "RouteError", "api_request", "credential_status", "demand", "estimate_cost",
    "ledger_path", "load_credentials", "load_routes", "maps", "route_for",
    "serp", "total_cost", "write_json", "__version__",
]
