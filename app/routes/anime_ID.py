from fastapi import APIRouter, HTTPException, Path, Request
import requests
from typing import Any, Dict
from app.services.anilist_service import fetch_anime_details
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.structure.details import structureAnilistDetails
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}")
async def animeInfo(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    try:
        data = fetch_anime_details(id)
        idSub = await fetch_malsyn_data_and_get_provider(data["id"])
        detailsData = structureAnilistDetails({"data": data, "idSub": idSub})
        return success_response(request, data=detailsData)
    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))
    except RuntimeError as e:
        return error_response(request, status_code=500, message="Runtime error", error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
