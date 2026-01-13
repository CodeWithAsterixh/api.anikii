from fastapi import APIRouter, Query, Request
from typing import Any, Dict, List
from app.services.anilist_discovery_service import fetch_search
from app.models.responses import AnimeItem
from app.helpers.response_envelope import success_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter()

@router.get("/search")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def search(request: Request, keyword: str = Query(..., min_length=1, max_length=100)) -> Dict[str, Any]:
    structured_data = await fetch_search(keyword)
    meta = {"search": {"keyword": keyword, "count": len(structured_data)}}
    return success_response(request, data=structured_data, meta=meta)