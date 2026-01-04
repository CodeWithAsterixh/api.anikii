from typing import Any, Dict
from app.queries.query_manager import query_manager
from app.helpers.fetchHelpers import make_api_request_async
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.getEpM3u8BasedGogo import get_episode

async def get_stream_data(id: int) -> Dict[str, Any]:
    """Fetch raw stream metadata from AniList."""
    query = query_manager.get_query("stream", "get_stream_data")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    return response["data"]["Media"]

async def get_episode_extra(id: int, ep: int) -> Dict[str, Any]:
    """Fetch combined extra info for sub/dub episodes."""
    query = query_manager.get_query("stream", "get_stream_data")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    
    data = response["data"]["Media"]
    title = ''
    thumbnail = ''
    if data.get("streamingEpisodes") and len(data["streamingEpisodes"]) > 0:
        index = ep - 1 if 0 <= ep - 1 < len(data["streamingEpisodes"]) else 0
        title = data["streamingEpisodes"][index].get("title", "")
        thumbnail = data["streamingEpisodes"][index].get("thumbnail", "")
    
    idSub = await fetch_malsyn_data_and_get_provider(id)
    gogoId = idSub.get("id_provider", {}).get("idGogo")
    gogoIdDub = idSub.get("id_provider", {}).get("idGogoDub")
    
    episode_sub = await get_episode(gogoId, ep) if gogoId else {}
    episode_dub = await get_episode(gogoIdDub, ep) if gogoIdDub else {}
    
    return {
        "episodesSub": episode_sub,
        "episodesDub": episode_dub,
        "animeInfo": {
            "title": title,
            "thumbnail": thumbnail,
            "episodes": {
                "currentEpisode": ep,
                "lastEpisode": data.get("episodes"),
            }
        },
        "meta": {
            "episode": ep,
            "hasSub": bool(episode_sub),
            "hasDub": bool(episode_dub),
        }
    }
