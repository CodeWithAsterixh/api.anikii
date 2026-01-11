from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.services.fyp_service import get_fyp_recommendations
from app.helpers.response_envelope import success_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/fyp", tags=["fyp"])

class FYPRequest(BaseModel):
    collection: List[str] = Field(..., min_items=1)

@router.post("")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_fyp(
    request: Request, 
    fyp_request: FYPRequest, 
    page: int = Query(1, ge=1, le=50)
) -> Dict[str, Any]:
    """Fetch personalized recommendations based on a collection of anime IDs."""
    recommendations = await get_fyp_recommendations(fyp_request.collection, page)
    meta = {
        "fyp": {
            "count": len(recommendations),
            "ids": fyp_request.collection,
            "page": page
        }
    }
    return success_response(request, data=recommendations, meta=meta)
