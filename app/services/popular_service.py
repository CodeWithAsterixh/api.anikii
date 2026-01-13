from typing import Any, Dict, List, Optional, Tuple
import httpx
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import run_cache_data, save_cache_data
from app.helpers.timeFunction import this_when, get_current_season

async def fetch_paged_media(
    query_category: str, 
    query_name: str, 
    cache_key: str, 
    page: int, 
    variables: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Generic helper to fetch paged media with caching."""
    cached = await run_cache_data(page, cache_key)
    if cached:
        return cached.get("page_info", {}), cached.get("data", [])

    query = query_manager.get_query(query_category, query_name)
    required_inputs = variables or {}
    required_inputs["page"] = page
    
    body = {"query": query, "variables": required_inputs}
    response = await make_api_request_async(body)
    
    if response.get("errors"):
        raise RuntimeError(response["errors"])
        
    media = response["data"]["Page"]["media"]
    page_info = response["data"]["Page"]["page_info"]
    
    await save_cache_data(page_info, media, cache_key, page)
    return page_info, media

async def get_popular(page: int):
    return await fetch_paged_media("popular", "get_popular_media", "popular", page)

async def get_popular_releases(page: int):
    return await fetch_paged_media("releases", "get_releases", "popular_releases", page)

async def get_popular_releases_seasons(page: int, season: Optional[str] = None, year: Optional[int] = None):
    season = season or get_current_season()
    year = year or this_when.year
    variables = {"season": season, "year": year}
    cache_key = f"popular_releases_seasons_{season}_{year}"
    return await fetch_paged_media("releases", "get_releases", cache_key, page, variables)

async def get_popular_upcoming(page: int):
    return await fetch_paged_media("upcoming", "get_upcoming", "popular_upcoming", page)
