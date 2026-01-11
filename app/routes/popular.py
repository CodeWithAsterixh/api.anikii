from fastapi import APIRouter, Query, Request
from typing import Any, Dict, Optional
from app.services.popular_service import (
    get_popular, 
    get_popular_releases, 
    get_popular_releases_seasons, 
    get_popular_upcoming
)
from app.helpers.response_envelope import success_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/popular", tags=["popular"])

@router.get("")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def popular(request: Request, page: int = Query(1, ge=1, le=50)) -> Dict[str, Any]:
    page_info, media = await get_popular(page)
    return success_response(request, data=media, meta={"pagination": page_info})

@router.get("/releases")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def popular_releases(request: Request, page: int = Query(1, ge=1)) -> Dict[str, Any]:
    page_info, media = await get_popular_releases(page)
    return success_response(request, data=media, meta={"pagination": page_info})

@router.get("/releases/seasons")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def popular_releases_seasons(
    request: Request, 
    page: int = Query(1, ge=1),
    season: Optional[str] = Query(None),
    year: Optional[int] = Query(None)
) -> Dict[str, Any]:
    page_info, media = await get_popular_releases_seasons(page, season, year)
    return success_response(request, data=media, meta={"pagination": page_info})

@router.get("/upcoming")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def popular_upcoming(request: Request, page: int = Query(1, ge=1)) -> Dict[str, Any]:
    page_info, media = await get_popular_upcoming(page)
    return success_response(request, data=media, meta={"pagination": page_info})
