from typing import Any, Dict, List
from app.queries.query_manager import query_manager
from app.helpers.fetchHelpers import make_api_request_async
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.getEpM3u8BasedGogo import get_episode, BASE_URLS
from app.helpers.gogo_episodes import scrape_gogo_episode_list, get_highest_episode, get_max_episodes_from_gogo

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
    
    # Map servers to stream_links for frontend compatibility
    # Also support grouped servers if available
    def process_episode_links(episode_data):
        if not episode_data:
            return
            
        links = []
        if episode_data.get("stream"):
            links.append({"name": "HLS Stream", "url": episode_data["stream"]})
            
        # Add grouped servers if available
        grouped = episode_data.get("grouped_servers", {})
        if grouped:
            for group_name, group_links in grouped.items():
                if group_links:
                    # Use a dict to ensure uniqueness by name (case-insensitive)
                    unique_group_links = {}
                    for k, v in group_links.items():
                        name_upper = k.upper()
                        if name_upper not in unique_group_links:
                            unique_group_links[name_upper] = {"name": k, "url": v}
                    
                    group_list = list(unique_group_links.values())
                    episode_data[f"links_{group_name.lower()}"] = group_list
                    
                    # For backward compatibility, also put them in stream_links if it's the main group
                    if group_name == "SUB":
                        for link in group_list:
                            if not any(l["name"].upper() == link["name"].upper() for l in links):
                                links.append(link)
                    elif group_name == "DUB" and not episode_data.get("stream_links"):
                        for link in group_list:
                            if not any(l["name"].upper() == link["name"].upper() for l in links):
                                links.append(link)
        elif "servers" in episode_data:
            unique_servers = {}
            for k, v in episode_data["servers"].items():
                name_upper = k.upper()
                if name_upper not in unique_servers:
                    unique_servers[name_upper] = {"name": k, "url": v}
            links.extend(list(unique_servers.values()))
            
        episode_data["stream_links"] = links

    process_episode_links(episode_sub)
    process_episode_links(episode_dub)
    
    # Also fetch the full list of episodes and max episode count
    episodes_list = await get_anime_episodes(id)
    total_episodes = await get_anime_max_episodes(id)
    if total_episodes == 0:
        total_episodes = data.get("episodes", 0)
    
    return {
        "episodesSub": episode_sub,
        "episodesDub": episode_dub,
        "episodesList": episodes_list,
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

async def get_anime_max_episodes(id: int) -> int:
    """Fetch the maximum episode number for an anime from GogoAnime."""
    idSub = await fetch_malsyn_data_and_get_provider(id)
    gogoId = idSub.get("id_provider", {}).get("idGogo")
    if not gogoId:
        return 0

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
        url = urljoin(base_url, gogoId)
        if "gogoanimez.cc/watch/" in base_url and not url.endswith("/"):
             url += "/"
             
        if "gogoanimez.cc/watch/" in base_url:
            urls_to_try = [url, f"{url.rstrip('/')}-episode-1"]
        else:
            urls_to_try = [f"{base_url.rstrip('/')}/{gogoId}-episode-1"]

        for target_url in urls_to_try:
            # Use the unified tool
            max_ep = await get_max_episodes_from_gogo(target_url)
            if max_ep > 0:
                return max_ep
            
    return 0

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
