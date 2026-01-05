from typing import Any, Dict, List
from app.queries.query_manager import query_manager
from app.helpers.fetchHelpers import make_api_request_async
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.getEpM3u8BasedGogo import get_episode, BASE_URLS
from app.helpers.gogo_episodes import scrape_gogo_episode_list, get_highest_episode

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
    
    # Also fetch the full list of episodes
    episodes_list = await get_anime_episodes(id)
    total_episodes = get_highest_episode(episodes_list) if episodes_list else data.get("episodes")
    
    return {
        "episodesSub": episode_sub,
        "episodesDub": episode_dub,
        "episodesList": episodes_list,
        "animeInfo": {
            "title": title,
            "thumbnail": thumbnail,
            "episodes": {
                "currentEpisode": total_episodes,
                "lastEpisode": total_episodes,
            }
        },
        "meta": {
            "episode": ep,
            "hasSub": bool(episode_sub),
            "hasDub": bool(episode_dub),
        }
    }

async def get_anime_episodes(id: int) -> List[Dict[str, Any]]:
    """Fetch the full list of episodes for an anime from GogoAnime."""
    idSub = await fetch_malsyn_data_and_get_provider(id)
    gogoId = idSub.get("id_provider", {}).get("idGogo")
    if not gogoId:
        return []

    from urllib.parse import urljoin
    
    # Try preferred domains first
    preferred_domains = [
        "https://gogoanimez.cc/watch/",
        "https://www14.gogoanimes.fi/"
    ]
    
    # Also include others from BASE_URLS
    other_domains = [url for url in BASE_URLS if url not in preferred_domains]
    all_domains = preferred_domains + other_domains

    for base_url in all_domains:
        # Construct URL for episode 1 (or any episode) to get the list container
        # Use gogoId as is, the slug is already correct
        url = urljoin(base_url, gogoId)
        
        # If the URL doesn't end with a slash, add it if it's a "watch" domain
        if "gogoanimez.cc/watch/" in base_url and not url.endswith("/"):
             url += "/"
             
        # For domains like gogoanimez.cc/watch/, they might need an episode suffix to show the list
        if "gogoanimez.cc/watch/" in base_url:
            # Try both the base anime URL and episode 1 URL
            urls_to_try = [url, f"{url.rstrip('/')}-episode-1"]
        else:
            urls_to_try = [f"{base_url.rstrip('/')}/{gogoId}-episode-1"]

        for target_url in urls_to_try:
            episodes = await scrape_gogo_episode_list(target_url)
            if episodes:
                return episodes
            
    return []
