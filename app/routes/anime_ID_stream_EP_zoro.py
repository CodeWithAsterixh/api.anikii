from fastapi import APIRouter, HTTPException
from app.helpers.scrapers.stream_scraper import get_stream
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.modules import fetch_malsyn_data_and_get_provider


router = APIRouter(prefix="/anime", tags=["streaming"])

@router.get("/{id}/stream/ep/{ep}/zoro")
async def fetch_streaming_info(id: int, ep: int):
    try:
        # Retrieve the GraphQL query
        query = query_manager.get_query("stream", "get_stream_data")

        # Define variables for the GraphQL query
        variables = {"id": id}

        # Prepare the API request body
        body = {
            "query": query,
            "variables": variables,
        }

        # Make the API request to retrieve anime data
        response = make_api_request(body)
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])

        data = response["data"]["Media"]

        # Fetch the Zoro ID
        idSub = await fetch_malsyn_data_and_get_provider(id)
        zoroId = idSub.get("id_provider", {}).get("idZoro")
        if not zoroId:
            raise HTTPException(status_code=404, detail="Zoro ID not found")

        # Generate episode IDs for sub and dub
        idSp = zoroId.split("-")[-1]
        episode_id_sub = f"{idSp}$episode${ep}$sub"
        episode_id_dub = f"{idSp}$episode${ep}$dub"
        print(episode_id_sub)
        print(episode_id_dub)

        # Fetch streaming data for sub
        try:
            stream_data_sub = await get_stream(episode_id_sub)
        except Exception as e:
            stream_data_sub = {"error": f"Error fetching sub stream: {str(e)}"}

        # Fetch streaming data for dub
        try:
            stream_data_dub = await get_stream(episode_id_dub)
        except Exception as e:
            stream_data_dub = {"error": f"Error fetching dub stream: {str(e)}"}

        # Combine results into response object
        result = {
            "streamingEpisodesSub": stream_data_sub,
            "streamingEpisodesDub": stream_data_dub,
            "animeInfo": {
                "title": data.get("title", {}).get("romaji"),
                "episodes": len(data.get("streamingEpisodes", [])),
            },
        }

        return {"result": result}, 200

    except Exception as e:
        # Handle unforeseen errors
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
