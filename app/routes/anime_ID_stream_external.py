from fastapi import APIRouter, HTTPException, Query, Request
from app.helpers.fetchHelpers import make_api_request
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/stream/external")
async def fetch_streaming_info(request: Request, id: int, type: str = Query("sub", description="Type of episode: 'sub' or 'dub'")):
    try:
        # Fetch provider data (sub and dub IDs)
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoSub = idSub["id_provider"]["idGogo"]

        # Construct URLs for sub and dub episodes
        urlSub = f"{BASEURL}/{gogoSub}-episode-1"

        # Fetch and parse streaming info for Sub
        try:
            episode_dataSub = await parse_streaming_info(urlSub)
        except Exception as e:
            return success_response(request, data={"error": "Sub episode not found", "episode": 1})

        return success_response(request, data=episode_dataSub)

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
