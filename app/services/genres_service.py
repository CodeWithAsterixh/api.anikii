from typing import List, Dict, Any, Optional
from app.services.anilist_discovery_service import fetch_genres
from app.helpers.json.cacheData import run_cache_data, save_cache_data
from app.helpers.json.json_writer import json_write
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager

async def get_genres_list() -> List[str]:
    """Fetch the list of all available genres."""
    cache_data_available = await run_cache_data(None, "genres")
    if cache_data_available is not None:
        return cache_data_available
    
    collection = await fetch_genres()
    data = await json_write("genres", collection)
    return data

async def get_genre_items(genre: str, page: int = 1) -> Dict[str, Any]:
    """Fetch media items for a specific genre with pagination."""
    cache_data_available = await run_cache_data(page, f"genres_{genre}")
    if cache_data_available:
        return {
            "data": cache_data_available.get("data"),
            "page_info": cache_data_available.get("page_info")
        }
    
    query = query_manager.get_query("genre_item", "get_genre_item")
    variables = {"genre": genre, "page": page}
    body = {"query": query, "variables": variables}
    
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    
    page_info = response["data"]["Page"]["page_info"]
    media = response["data"]["Page"]["media"]
    
    await save_cache_data(page_info, media, f"genres_{genre}", page)
    
    return {
        "data": media,
        "page_info": page_info
    }
