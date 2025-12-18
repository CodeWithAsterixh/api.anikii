from fastapi import APIRouter, HTTPException, Path, Request
import requests
from typing import Any, Dict
from app.services.anilist_service import fetch_anime_relations
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["relations"])

@router.get("/{id}/relations")
async def animeRelations(request: Request, id: int = Path(..., ge=1)) -> Dict[str, Any]:
    try:
        relations = fetch_anime_relations(id)
        meta = {"anime": {"id": id}}
        return success_response(request, data=relations, meta=meta)
    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except RuntimeError as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
    except Exception as e:
        return error_response(request, status_code=500, message=str(e), error=str(e))
