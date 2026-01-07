from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.helpers.getSubOrDub import get_episode_data
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.base import BASEURL

async def get_episode_stream(id: int, ep: int, type: str = "sub", provider: Optional[str] = None) -> Dict[str, Any]:
    """Resolve streaming info for an episode."""
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
