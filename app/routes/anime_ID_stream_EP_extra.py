from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.getEpM3u8BasedGogo import get_episode

router = APIRouter(prefix="/anime", tags=["id", "ep"])

@router.get("/{id}/stream/ep/{ep}/extra")
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
        response = make_api_request(body)  # Ensure `make_api_request` is async
        if response.get("errors"):
            print("there is error from line 27 in this route")
            raise HTTPException(status_code=500, detail=response["errors"])

        data = response["data"]["Media"]
        

        # Fetch the Zoro ID
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoId = idSub.get("id_provider", {}).get("idGogo")
        gogoIdDub = idSub.get("id_provider", {}).get("idGogoDub")
        if not gogoId or not gogoIdDub:
            raise HTTPException(status_code=404, detail="ID not found")

        # Generate episode data for sub and dub
        try:
            episode_sub = await get_episode(gogoId, ep)
            episode_dub = await get_episode(gogoIdDub, ep)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching episodes: {str(e)}")

        # Combine results into response object
        result = {
            "episodesSub": episode_sub,
            "episodesDub": episode_dub,
            "animeInfo": {
                "title": data.get("title", {}),
                "episodes":{
                    "currentEpisode":ep,
                    "lastEpisode":data.get("episodes", {}),
                }                 
            },
        }

        return {"result": result}

    except HTTPException as http_ex:
        # Re-raise HTTP exceptions with proper status codes
        raise http_ex

    except Exception as e:
        # Handle unforeseen errors
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
