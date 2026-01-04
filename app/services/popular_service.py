from typing import Any, Dict, List, Optional, Tuple
import httpx
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import runCacheData, saveCacheData
from app.helpers.timeFunction import this_when, get_current_season

async def fetch_paged_media(
    query_category: str, 
    query_name: str, 
    cache_key: str, 
    page: int, 
    variables: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Generic helper to fetch paged media with caching."""
    cached = runCacheData(page, cache_key)
    if cached:
        return cached.get("pageInfo", {}), cached.get("data", [])

    query = query_manager.get_query(query_category, query_name)
    vars = variables or {}
    vars["page"] = page
    
    body = {"query": query, "variables": vars}
    response = await make_api_request_async(body)
    
    if response.get("errors"):
        raise RuntimeError(response["errors"])
        
    media = response["data"]["Page"]["media"]
    pageInfo = response["data"]["Page"]["pageInfo"]
    
    saveCacheData(pageInfo, media, cache_key, page)
    return pageInfo, media

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
    return await fetch_paged_media("upcoming", "get_upcoming_media", "popular_upcoming", page)
