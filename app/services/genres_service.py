from typing import List, Dict, Any, Optional
from app.services.anilist_discovery_service import fetch_genres
from app.helpers.json.cacheData import runCacheData, saveCacheData
from app.helpers.json.json_writer import jsonWrite
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager

async def get_genres_list() -> List[str]:
    """Fetch the list of all available genres."""
    cacheDataAvailable = runCacheData(None, "genres")
    if cacheDataAvailable is not None:
        return cacheDataAvailable
    
    collection = await fetch_genres()
    data = jsonWrite("genres", collection)
    return data

async def get_genre_items(genre: str, page: int = 1) -> Dict[str, Any]:
    """Fetch media items for a specific genre with pagination."""
    cacheDataAvailable = runCacheData(page, f"genres_{genre}")
    if cacheDataAvailable:
        return {
            "data": cacheDataAvailable.get("data"),
            "pageInfo": cacheDataAvailable.get("pageInfo")
        }
    
    query = query_manager.get_query("genre_item", "get_genre_item")
    variables = {"genre": genre, "page": page}
    body = {"query": query, "variables": variables}
    
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    
    pageInfo = response["data"]["Page"]["pageInfo"]
    media = response["data"]["Page"]["media"]
    
    saveCacheData(pageInfo, media, f"genres_{genre}", page)
    
    return {
        "data": media,
        "pageInfo": pageInfo
    }
