from fastapi import APIRouter, HTTPException, Path, Query, Request
import httpx
from typing import Any, Dict
from app.services.anilist_service import fetch_recommended
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["recommended"])

@router.get("/{id}/recommended")
async def animeRecommended(
    request: Request,
    id: int = Path(..., ge=1),
    page: int = Query(1, ge=1, le=50)
) -> Dict[str, Any]:
    try:
        recommended = await fetch_recommended(id, page)
        meta = {"anime": {"id": id}, "pagination": recommended.get("pageInfo")}
        return success_response(request, data=recommended.get("recommendations"), meta=meta)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except RuntimeError as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
