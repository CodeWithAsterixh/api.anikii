from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.helpers.getSubOrDub import get_episode_data
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.base import BASEURL
from app.helpers.getEpM3u8BasedGogo import get_episode
from app.services.stream_metadata_service import get_anime_max_episodes
from app.queries.query_manager import query_manager
from app.helpers.fetchHelpers import make_api_request_async

async def get_stream_data(id: int) -> Dict[str, Any]:
    """Fetch raw stream metadata from AniList."""
    query = query_manager.get_query("stream", "get_stream_data")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    return response["data"]["Media"]

async def get_episode_stream(id: int, ep: int, type: str = "sub") -> Dict[str, Any]:
    """Resolve streaming info for an episode."""
    episode_data = await get_episode_data(id, ep, type)
    if not episode_data:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode_data

async def get_episode_dub(id: int, ep: int) -> Dict[str, Any]:
    """Fetch dub streaming info."""
    id_sub = await fetch_malsyn_data_and_get_provider(id)
    gogo_dub = id_sub["id_provider"].get("idGogoDub")
    if not gogo_dub:
         return {"error": "Dub ID not found", "episode": ep}
    url_dub = f"{BASEURL}/{gogo_dub}-episode-{ep}"
    try:
        return await parse_streaming_info(url_dub)
    except Exception:
        return {"error": "Dub episode not found", "episode": ep}

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
    
    id_sub = await fetch_malsyn_data_and_get_provider(id)
    gogo_id = id_sub.get("id_provider", {}).get("idGogo")
    gogoid_dub = id_sub.get("id_provider", {}).get("idGogoDub")
    
    episode_sub = await get_episode(gogo_id, ep) if gogo_id else {}
    episode_dub = await get_episode(gogoid_dub, ep) if gogoid_dub else {}
    
    # Scrape total episodes from GogoAnime using the unified tool
    total_episodes = await get_anime_max_episodes(id)
    if total_episodes == 0:
        total_episodes = data.get("episodes", 0)
    
    return {
        "episodesSub": episode_sub,
        "episodesDub": episode_dub,
        "animeInfo": {
            "title": title,
            "thumbnail": thumbnail,
            "episodes": {
                "currentEpisode": ep,
                "lastEpisode": total_episodes,
            }
        },
        "meta": {
            "episode": ep,
            "hasSub": bool(episode_sub),
            "hasDub": bool(episode_dub),
        }
    }

async def get_external_stream(id: int) -> Dict[str, Any]:
    """Fetch external streaming info for the first episode."""
    id_sub = await fetch_malsyn_data_and_get_provider(id)
    gogo_sub = id_sub["id_provider"].get("idGogo")
    if not gogo_sub:
         return {"error": "Gogo ID not found", "episode": 1}
    url_sub = f"{BASEURL}/{gogo_sub}-episode-1"
    try:
        return await parse_streaming_info(url_sub)
    except Exception:
        return {"error": "Sub episode not found", "episode": 1}
