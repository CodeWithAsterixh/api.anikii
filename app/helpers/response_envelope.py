from __future__ import annotations
from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Request


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_request_info(request: Request) -> Dict[str, Any]:
    """Collect request metadata for the response envelope."""
    try:
        scope = request.scope
        method = scope.get("method")
        path = scope.get("path")
        # Query dict
        query_params = dict(request.query_params)
    except Exception:
        method = None
        path = None
        query_params = {}

    # Prefer an incoming request id header if provided
    req_id = request.headers.get("x-request-id") or str(uuid4())

    return {
        "id": req_id,
        "timestamp": _iso_utc_now(),
        "method": method,
        "path": path,
        "query": query_params,
    }


def success_response(
    request: Request,
    data: Any,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    message: str = "OK",
) -> Dict[str, Any]:
    """Build a standardized success response envelope."""
    return {
        "status": {
            "code": status_code,
            "success": True,
            "message": message,
        },
        "request": get_request_info(request),
        "meta": meta or {},
        "data": data,
    }


def error_response(
    request: Request,
    status_code: int,
    message: str,
    error: Optional[Any] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a standardized error response envelope."""
    body: Dict[str, Any] = {
        "status": {
            "code": status_code,
            "success": False,
            "message": message,
        },
        "request": get_request_info(request),
        "meta": meta or {},
        "data": None,
    }
    if error is not None:
        body["error"] = error
    return body