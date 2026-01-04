from fastapi import APIRouter, HTTPException, Query, Request
import httpx
from typing import Any, Dict, List
from app.services.anilist_discovery_service import fetch_search
from app.models.responses import AnimeItem
from app.helpers.response_envelope import success_response, error_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter()

@router.get("/search")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def search(request: Request, keyword: str = Query(..., min_length=1, max_length=100)) -> Dict[str, Any]:
    try:
        structuredData = await fetch_search(keyword)
        meta = {"search": {"keyword": keyword, "count": len(structuredData)}}
        return success_response(request, data=structuredData, meta=meta)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except RuntimeError as e:
        # Handle AniList GraphQL errors raised by the service
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
