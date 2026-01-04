from fastapi import APIRouter, Request, Path, Query
from typing import Any, Dict
from app.services.genres_service import get_genres_list, get_genre_items
from app.helpers.response_envelope import success_response, error_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/genres", tags=["genres"])

@router.get("")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def list_genres(request: Request) -> Dict[str, Any]:
    """Fetch the list of all available genres."""
    try:
        data = await get_genres_list()
        meta = {"cache": {"source": "tmp", "type": "list"}}
        return success_response(request, data=data, meta=meta)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch genres", error=str(e))

@router.get("/{genre}")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_genre_media(
    request: Request, 
    genre: str = Path(..., min_length=1), 
    page: int = Query(1, ge=1)
) -> Dict[str, Any]:
    """Fetch media items for a specific genre with pagination."""
    try:
        result = await get_genre_items(genre, page)
        meta = {"pagination": result.get("pageInfo")}
        return success_response(request, data=result.get("data"), meta=meta)
    except Exception as e:
        return error_response(request, status_code=500, message=f"Failed to fetch items for genre: {genre}", error=str(e))
