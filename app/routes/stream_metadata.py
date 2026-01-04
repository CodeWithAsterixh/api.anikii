from fastapi import APIRouter, Path, Query, Request, HTTPException
from typing import Any, Dict, Optional
from app.services.stream_metadata_service import get_stream_data, get_episode_extra
from app.services.stream_resolver_service import get_episode_stream, get_episode_dub, get_external_stream
from app.helpers.response_envelope import success_response, error_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/anime", tags=["stream-metadata"])

@router.get("/{id}/stream")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_anime_stream_metadata(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    """Fetch streaming metadata for an anime."""
    try:
        data = await get_stream_data(id)
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch stream metadata", error=str(e))

@router.get("/{id}/stream/ep/{ep}")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_episode_streaming_info(
    request: Request,
    id: int = Path(..., ge=1),
    ep: int = Path(..., ge=1),
    type: str = Query("sub", regex="^(sub|dub)$"),
    provider: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Fetch streaming info for a specific episode."""
    try:
        data = await get_episode_stream(id, ep, type, provider)
        return success_response(request, data=data)
    except HTTPException as e:
        return error_response(request, status_code=e.status_code, message=e.detail)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch episode stream info", error=str(e))

@router.get("/{id}/stream/ep/{ep}/dub")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_episode_dub_info(
    request: Request,
    id: int = Path(..., ge=1),
    ep: int = Path(..., ge=1)
) -> Dict[str, Any]:
    """Fetch dub info for an episode."""
    try:
        data = await get_episode_dub(id, ep)
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch dub info", error=str(e))

@router.get("/{id}/stream/ep/{ep}/extra")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_episode_extra_info(
    request: Request,
    id: int = Path(..., ge=1),
    ep: int = Path(..., ge=1)
) -> Dict[str, Any]:
    """Fetch extra info for an episode (sub/dub combined)."""
    try:
        result = await get_episode_extra(id, ep)
        return success_response(request, data=result, meta=result.get("meta"))
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch extra info", error=str(e))

@router.get("/{id}/stream/external")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_external_streaming_info(
    request: Request,
    id: int = Path(..., ge=1),
    type: str = Query("sub", regex="^(sub|dub)$")
) -> Dict[str, Any]:
    """Fetch external streaming info."""
    try:
        data = await get_external_stream(id, type)
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch external stream info", error=str(e))
