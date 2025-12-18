from fastapi import APIRouter, HTTPException, Request
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL

import requests
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["id", "ep"])

@router.get("/{id}/stream/ep/{ep}/dub")
async def fetch_streaming_info(request: Request, id: int, ep: int):
    try:

        # Fetch provider data (sub and dub IDs)
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoDub = idSub["id_provider"]["idGogoDub"]

        # Construct URLs for sub and dub episodes
        urlDub = f"{BASEURL}/{gogoDub}-episode-{ep}"

        # Fetch and parse streaming info for Dub
        try:
            episode_dataDub = parse_streaming_info(urlDub)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                episode_dataDub = {"error": "Dub episode not found", "episode": ep}
            else:
                raise

        return success_response(request, data=episode_dataDub)

    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
