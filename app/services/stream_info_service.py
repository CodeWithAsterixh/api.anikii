from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.helpers.getSubOrDub import get_episode_data
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.services.anime_downloader_service import resolve_stream_with_anime_downloader
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.base import BASEURL
from app.helpers.getEpM3u8BasedGogo import get_episode
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

async def get_episode_stream(id: int, ep: int, type: str = "sub", provider: Optional[str] = None) -> Dict[str, Any]:
    """Resolve streaming info for an episode, trying anime-downloader first."""
    episode_data = await resolve_stream_with_anime_downloader(id, ep, type, provider_override=provider)
    if not episode_data:
        episode_data = await get_episode_data(id, ep, type)
    if not episode_data:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode_data

async def get_episode_dub(id: int, ep: int) -> Dict[str, Any]:
    """Fetch dub streaming info."""
    idSub = await fetch_malsyn_data_and_get_provider(id)
    gogoDub = idSub["id_provider"].get("idGogoDub")
    if not gogoDub:
         return {"error": "Dub ID not found", "episode": ep}
    urlDub = f"{BASEURL}/{gogoDub}-episode-{ep}"
    try:
        return await parse_streaming_info(urlDub)
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

async def get_external_stream(id: int, type: str = "sub") -> Dict[str, Any]:
    """Fetch external streaming info for the first episode."""
    idSub = await fetch_malsyn_data_and_get_provider(id)
    gogoSub = idSub["id_provider"].get("idGogo")
    if not gogoSub:
         return {"error": "Gogo ID not found", "episode": 1}
    urlSub = f"{BASEURL}/{gogoSub}-episode-1"
    try:
        return await parse_streaming_info(urlSub)
    except Exception:
        return {"error": "Sub episode not found", "episode": 1}
