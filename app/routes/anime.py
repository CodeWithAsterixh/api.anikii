from fastapi import APIRouter, Path, Query, Request
from typing import Any, Dict, Optional
from app.services.anilist_media_service import (
    fetch_anime_details,
    fetch_anime_relations,
    fetch_characters,
    fetch_recommended,
    fetch_trailers
)
from app.services.stream_metadata_service import get_anime_episodes, get_anime_max_episodes
from app.helpers.gogo_episodes import get_highest_episode, get_max_episodes_from_gogo
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.structure.anime_details import structureAnilistDetails
from app.helpers.response_envelope import success_response, error_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/anime", tags=["anime"])

@router.get("/{id}")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_anime_info(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    """Fetch basic anime details."""
    try:
        data = await fetch_anime_details(id)
        idSub = await fetch_malsyn_data_and_get_provider(data["id"])
        
        # Scrape total episodes from GogoAnime using the unified tool
        total_episodes = await get_anime_max_episodes(id)
        if total_episodes == 0:
            total_episodes = data.get("episodes", 0)
        
        detailsData = structureAnilistDetails({"data": data, "idSub": idSub})
        
        # Replace the current episode value (total length)
        
        detailsData = {
            **detailsData,
            "episodes":total_episodes
        }
        
        return success_response(request, data=detailsData)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch anime details", error=str(e))

@router.get("/{id}/relations")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_anime_relations(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    """Fetch anime relations."""
    try:
        data = await fetch_anime_relations(id)
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch anime relations", error=str(e))

@router.get("/{id}/characters")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_anime_characters(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    """Fetch anime characters."""
    try:
        data = await fetch_characters(id)
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch anime characters", error=str(e))

@router.get("/{id}/recommended")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_anime_recommended(
    request: Request, 
    id: int = Path(..., ge=1),
    page: int = Query(1, ge=1)
) -> Dict[str, Any]:
    """Fetch recommended anime based on ID."""
    try:
        result = await fetch_recommended(id, page)
        return success_response(
            request, 
            data=result["recommendations"], 
            meta={"pagination": result["pageInfo"]}
        )
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch recommendations", error=str(e))

@router.get("/{id}/trailers")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_anime_trailers(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    """Fetch anime trailers."""
    try:
        data = await fetch_trailers(id)
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to fetch trailers", error=str(e))
