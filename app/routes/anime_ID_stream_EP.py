from fastapi import APIRouter, HTTPException
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL

import requests

router = APIRouter(prefix="/anime", tags=["id", "ep"])

@router.get("/{id}/stream/ep/{ep}")
async def fetch_streaming_info(id: int, ep: int):
    try:
        # Fetch provider data (sub and dub IDs)
        idSub = await fetch_malsyn_data_and_get_provider(id)
        print(idSub)
        gogoSub = idSub["id_provider"]["idGogo"]

        # Construct URLs for sub and dub episodes
        urlSub = f"{BASEURL}/{gogoSub}-episode-{ep}"

        # Initialize result containers
        episode_dataSub = {}

        # Fetch and parse streaming info for Sub
        try:
            episode_dataSub = parse_streaming_info(urlSub)
        except requests.exceptions.HTTPError as e:            
            if e.response.status_code == 404:
                episode_dataSub = {"error": "Sub episode not found", "episode": ep}
            else:
                raise

        return episode_dataSub, 200

    except requests.exceptions.RequestException as e:
        # Handle general request errors
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        # Handle any unforeseen errors        
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
