from typing import Any, Dict, List
from app.core.constants import GOGO_PATH
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
    data = await _fetch_media_data(id)
    title, thumbnail = _extract_title_thumbnail(data, ep)
    gogo_ids = await _fetch_gogo_ids(id)
    episode_sub, episode_dub = await _fetch_episodes(gogo_ids, ep)
    _process_episode_links(episode_sub)
    _process_episode_links(episode_dub)
    episodes_list = await get_anime_episodes(id)
    total_episodes = await _get_total_episodes(id, data)
    return _build_response(episode_sub, episode_dub, episodes_list, title, thumbnail, ep, total_episodes)

async def _fetch_media_data(id: int) -> Dict[str, Any]:
    query = query_manager.get_query("stream", "get_stream_data")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    return response["data"]["Media"]

def _extract_title_thumbnail(data: Dict[str, Any], ep: int) -> tuple[str, str]:
    title, thumbnail = '', ''
    if data.get("streamingEpisodes") and 0 <= ep - 1 < len(data["streamingEpisodes"]):
        episode = data["streamingEpisodes"][ep - 1]
        title = episode.get("title", "")
        thumbnail = episode.get("thumbnail", "")
    return title, thumbnail

async def _fetch_gogo_ids(id: int) -> Dict[str, str]:
    id_sub = await fetch_malsyn_data_and_get_provider(id)
    return {
        "sub": id_sub.get("id_provider", {}).get("idGogo"),
        "dub": id_sub.get("id_provider", {}).get("idGogoDub")
    }

async def _fetch_episodes(gogo_ids: Dict[str, str], ep: int) -> tuple[Dict[str, Any], Dict[str, Any]]:
    episode_sub = await get_episode(gogo_ids["sub"], ep) if gogo_ids["sub"] else {}
    episode_dub = await get_episode(gogo_ids["dub"], ep) if gogo_ids["dub"] else {}
    return episode_sub, episode_dub

def _process_episode_links(episode_data: Dict[str, Any]) -> None:
    if not episode_data:
        return
    links = []
    if episode_data.get("stream"):
        links.append({"name": "HLS Stream", "url": episode_data["stream"]})
    _add_grouped_servers(episode_data, links)
    _add_servers(episode_data, links)
    episode_data["stream_links"] = links

def _add_grouped_servers(episode_data: Dict[str, Any], links: List[Dict[str, str]]) -> None:
    grouped = episode_data.get("grouped_servers", {})
    for group_name, group_links in grouped.items():
        if not group_links:
            continue
        unique_links = {k.upper(): {"name": k, "url": v} for k, v in group_links.items()}
        group_list = list(unique_links.values())
        episode_data[f"links_{group_name.lower()}"] = group_list
        if (group_name == "SUB" or group_name == "DUB") and not episode_data.get("stream_links"):
            links.extend([l for l in group_list if not any(x["name"].upper() == l["name"].upper() for x in links)])


def _add_servers(episode_data: Dict[str, Any], links: List[Dict[str, str]]) -> None:
    if "servers" not in episode_data or "grouped_servers" in episode_data:
        return
    unique_servers = {k.upper(): {"name": k, "url": v} for k, v in episode_data["servers"].items()}
    links.extend(list(unique_servers.values()))

async def _get_total_episodes(id: int, data: Dict[str, Any]) -> int:
    total = await get_anime_max_episodes(id)
    return total if total != 0 else data.get("episodes", 0)

def _build_response(sub: Dict[str, Any], dub: Dict[str, Any], episodes_list: List[Dict[str, Any]],
                    title: str, thumbnail: str, ep: int, total_episodes: int) -> Dict[str, Any]:
    return {
        "episodesSub": sub,
        "episodesDub": dub,
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
            "hasSub": bool(sub),
            "hasDub": bool(dub),
        }
    }

async def get_anime_max_episodes(id: int) -> int:
    """Fetch the maximum episode number for an anime from GogoAnime."""
    id_sub = await fetch_malsyn_data_and_get_provider(id)
    gogo_id = id_sub.get("id_provider", {}).get("idGogo")
    if not gogo_id:
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
        url = urljoin(base_url, gogo_id)
        if GOGO_PATH in base_url and not url.endswith("/"):
             url += "/"
             
        if GOGO_PATH in base_url:
            urls_to_try = [url, f"{url.rstrip('/')}-episode-1"]
        else:
            urls_to_try = [f"{base_url.rstrip('/')}/{gogo_id}-episode-1"]

        for target_url in urls_to_try:
            # Use the unified tool
            max_ep = await get_max_episodes_from_gogo(target_url)
            if max_ep > 0:
                return max_ep
            
    return 0

async def get_anime_episodes(id: int) -> List[Dict[str, Any]]:
    """Fetch the full list of episodes for an anime from GogoAnime."""
    id_sub = await fetch_malsyn_data_and_get_provider(id)
    gogo_id = id_sub.get("id_provider", {}).get("idGogo")
    if not gogo_id:
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
        # Use gogo_id as is, the slug is already correct
        url = urljoin(base_url, gogo_id)
        
        # If the URL doesn't end with a slash, add it if it's a "watch" domain
        if GOGO_PATH in base_url and not url.endswith("/"):
             url += "/"
             
        # For domains like gogoanimez.cc/watch/, they might need an episode suffix to show the list
        if GOGO_PATH in base_url:
            # Try both the base anime URL and episode 1 URL
            urls_to_try = [url, f"{url.rstrip('/')}-episode-1"]
        else:
            urls_to_try = [f"{base_url.rstrip('/')}/{gogo_id}-episode-1"]

        for target_url in urls_to_try:
            episodes = await scrape_gogo_episode_list(target_url)
            if episodes:
                return episodes
            
    return []
