from __future__ import annotations
from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Request
from app.core.config import get_settings


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
    settings = get_settings()
    
    # Hide error details in production unless explicitly allowed
    safe_message = message
    safe_error = error
    
    if not settings.DEBUG and status_code >= 500:
        safe_message = "Internal server error"
        safe_error = {"type": "InternalError"}

    body: Dict[str, Any] = {
        "status": {
            "code": status_code,
            "success": False,
            "message": safe_message,
        },
        "request": get_request_info(request),
        "meta": meta or {},
        "data": None,
    }
    if safe_error is not None:
        body["error"] = safe_error
    return body