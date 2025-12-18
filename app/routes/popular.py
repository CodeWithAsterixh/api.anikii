from fastapi import APIRouter, HTTPException, Query, Request
import requests
from typing import Any, Dict
from app.services.anilist_service import fetch_popular
from app.helpers.json.cacheData import runCacheData, saveCacheData
from app.models.responses import PagedResponse
from app.helpers.response_envelope import success_response, error_response

router = APIRouter()

@router.get("/popular")
def popular(request: Request, page: int = Query(1, ge=1, le=50)) -> Dict[str, Any]:
    try:
        cacheDataAvailable = runCacheData(page, "popular")
        if cacheDataAvailable is not None:
            # cacheDataAvailable already matches the old shape; wrap it
            meta = {"pagination": cacheDataAvailable.get("pageInfo")}
            return success_response(request, data=cacheDataAvailable.get("data"), meta=meta)
        pageInfo, media = fetch_popular(page)
        data = saveCacheData(pageInfo, media, "popular", page)
        meta = {"pagination": pageInfo}
        return success_response(request, data=media, meta=meta)
    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))
    except RuntimeError as e:
        return error_response(request, status_code=500, message="Runtime error", error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
