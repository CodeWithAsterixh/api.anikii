from fastapi import APIRouter, HTTPException, Request
import httpx
from typing import Any, Dict
from app.services.anilist_service import fetch_genres
from app.helpers.json.cacheData import runCacheData
from app.helpers.json.jsonParser import jsonWrite
from app.helpers.response_envelope import success_response, error_response


router = APIRouter()

@router.get("/genres")
async def genres(request: Request) -> Dict[str, Any]:
    try:
        cacheDataAvailable = runCacheData(None, "genres")
        if cacheDataAvailable is not None:
            # cache is a list of genres
            meta = {"cache": {"source": "tmp", "type": "list"}}
            return success_response(request, data=cacheDataAvailable, meta=meta)
        collection = await fetch_genres()
        data = jsonWrite("genres", collection)
        meta = {"cache": {"source": "tmp", "type": "list"}}
        return success_response(request, data=data, meta=meta)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))
    except RuntimeError as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
