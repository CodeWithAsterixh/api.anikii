from fastapi import APIRouter, HTTPException, Path, Request
import httpx
from typing import Any, Dict
from app.services.anilist_service import fetch_trailers
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["trailers"])

@router.get("/{id}/trailers")
async def animeTrailers(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    try:
        data = await fetch_trailers(id)
        return success_response(request, data=data)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except RuntimeError as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
