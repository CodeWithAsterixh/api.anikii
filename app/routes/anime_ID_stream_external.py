from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
import requests

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/stream/external")
async def fetch_streaming_info(id: int):
    try:
        # Retrieve the GraphQL query
        query = query_manager.get_query("stream", "get_stream_data")

        # Define variables for the GraphQL query
        variables = {"id": id}

        # Prepare the API request body
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request to retrieve anime data
        response = make_api_request(body)
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])

        data = response["data"]["Media"]

        # Fetch provider data (sub and dub IDs)
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoSub = idSub["id_provider"]["idGogo"]

        # Construct URLs for sub and dub episodes
        urlSub = f"https://anitaku.bz/{gogoSub}-episode-1"

        # Initialize result containers
        episode_dataSub = {}

        # Fetch and parse streaming info for Sub
        try:
            episode_dataSub = parse_streaming_info(urlSub)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                episode_dataSub = {"error": "Sub episode not found", "episode": 1}
            else:
                raise

        return {"result": episode_dataSub}, 200

    except requests.exceptions.RequestException as e:
        # Handle general request errors
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
