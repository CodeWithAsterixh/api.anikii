from typing import Any, Dict, List, Optional, Union
from app.helpers.json.json_loader import jsonLoad
from app.helpers.json.json_writer import json_save
from app.helpers.json.pageLocator import ensure_page_exists
from app.structure.listItem import structure_anilist_array
# Database helpers are imported lazily inside functions to avoid side effects during import time


from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()

async def run_cache_data(page: Optional[int], file_path: str, ttl: Optional[int] = None) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Return cached data if available and not expired.
    - If page is None, returns the entire cached object (e.g., dict for paginated caches or list for collections) or None.
    - If page is provided and exists, returns a dict with page_info and data for that page.
    - Returns None when cache is not available or expired for the requested page.
    """
    # Use global default TTL if not specified
    load_ttl = ttl if ttl is not None else settings.CACHE_TTL
    load_data = await jsonLoad(file_path, ttl=load_ttl)

    # If no specific page requested, return whatever is cached (may be dict or list)
    if page is None:
        return load_data if load_data else None

    # When a page is requested, ensure it exists in cache
    if isinstance(load_data, dict) and load_data and ensure_page_exists(load_data, page):
        last_page = load_data.get("last_page", 1)
        page_info = {
            "last_page": last_page,
            "currentPage": page,
        }
        data = load_data["pages"][str(page)]
        return {
            "page_info": page_info,
            "data": data,
        }

    # No cache available, caller should fetch from API
    return None


async def save_cache_data(page_info: Dict[str, Any], media: List[Dict[str, Any]], file_path: str, page: int) -> Dict[str, Any]:
    """
    Save the cache data for a given file and page.
    Returns the structured cached response dict with page_info and data.
    """
    structured_data = structure_anilist_array(media)

    # Cap last_page to a sane maximum (align with pagination constraints)
    last_page = min(page_info.get("last_page", 1), 50)
    page_info_out = {
        "last_page": last_page,
        "currentPage": page,
    }

    # Persist to DB if present (lazy import to avoid test-time DB dependency)
    try:
        from app.database.addFile import find_file_by_name, update_in_db  # type: ignore
        find_db = await find_file_by_name(f"{file_path}.json")
        if find_db:
            await update_in_db(f"{file_path}.json", {"$set": {f"data.pages.{page}": structured_data}})
            logger.info(f"Updated database cache for {file_path}.json")
    except Exception as e:
        # Skip DB persistence if unavailable
        logger.warning(f"Skipped database cache update for {file_path}: {e}")

    # Persist to JSON file
    await json_save(file_path, page, {"last_page": last_page, "data": structured_data})
    return {
        "page_info": page_info_out,
        "data": structured_data,
    }
    
    