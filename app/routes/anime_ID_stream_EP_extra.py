from fastapi import APIRouter, HTTPException, Request
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.getEpM3u8BasedGogo import get_episode
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["id", "ep"])

@router.get("/{id}/stream/ep/{ep}/extra")
async def fetch_streaming_info(request: Request, id: int, ep: int):
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
        response = await make_api_request_async(body)
        if response.get("errors"):
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])

        data = response["data"]["Media"]
        
        # extra info
        title = ''
        thumbnail = ''
        if len(data["streamingEpisodes"]) > 0:
            index = 0
            if ep - 1 >= 0 and ep - 1 < len(data["streamingEpisodes"]):
                index = ep-1
            else:
                index = 0
            title = data["streamingEpisodes"][index]["title"]
            thumbnail = data["streamingEpisodes"][index]["thumbnail"]
        

        # Fetch the Zoro ID
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoId = idSub.get("id_provider", {}).get("idGogo")
        gogoIdDub = idSub.get("id_provider", {}).get("idGogoDub")
        

        # Generate episode data for sub and dub
        episode_sub = {}
        episode_dub = {}
        
        if gogoId:
            try:
                episode_sub = await get_episode(gogoId, ep)
            except Exception as e:
                return error_response(request, status_code=500, message="Error fetching sub episode", error=str(e))
        if gogoIdDub:
            try:
                episode_dub = await get_episode(gogoIdDub, ep)
            except Exception as e:
                return error_response(request, status_code=500, message="Error fetching dub episode", error=str(e))

        # Combine results into response object
        result = {
            "episodesSub": episode_sub,
            "episodesDub": episode_dub,
            "animeInfo": {
                "title": title,
                "thumbnail": thumbnail,
                "episodes":{
                    "currentEpisode":ep,
                    "lastEpisode":data.get("episodes", {}),
                }                 
            },
        }
        meta = {
            "episode": ep,
            "hasSub": bool(episode_sub),
            "hasDub": bool(episode_dub),
        }

        return success_response(request, data=result, meta=meta)

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
