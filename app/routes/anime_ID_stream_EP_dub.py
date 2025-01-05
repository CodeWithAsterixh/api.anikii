from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
import requests

router = APIRouter(prefix="/anime", tags=["id", "ep"])

@router.get("/{id}/stream/ep/{ep}/dub")
async def fetch_streaming_info(id: int, ep: int):
    try:

        # Fetch provider data (sub and dub IDs)
        idSub = await fetch_malsyn_data_and_get_provider(id)
        print(1)
        gogoDub = idSub["id_provider"]["idGogoDub"]

        # Construct URLs for sub and dub episodes
        urlDub = f"https://anitaku.bz/{gogoDub}-episode-{ep}"

        # Initialize result containers
        episode_dataDub = {}

        # Fetch and parse streaming info for Dub
        try:
            episode_dataDub = parse_streaming_info(urlDub)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                episode_dataDub = {"error": "Dub episode not found", "episode": ep}
            else:
                raise

        

        return {"result": episode_dataDub}, 200

    except requests.exceptions.RequestException as e:
        # Handle general request errors
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
