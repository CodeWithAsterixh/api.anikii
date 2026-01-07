from typing import Any, Dict, List, Optional, Union
from app.helpers.json.json_loader import jsonLoad
from app.helpers.json.json_writer import jsonSave
from app.helpers.json.pageLocator import ensure_page_exists
from app.structure.listItem import structureAnilistArray
# Database helpers are imported lazily inside functions to avoid side effects during import time


from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()

async def runCacheData(page: Optional[int], filePath: str, ttl: Optional[int] = None) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Return cached data if available and not expired.
    - If page is None, returns the entire cached object (e.g., dict for paginated caches or list for collections) or None.
    - If page is provided and exists, returns a dict with pageInfo and data for that page.
    - Returns None when cache is not available or expired for the requested page.
    """
    # Use global default TTL if not specified
    load_ttl = ttl if ttl is not None else settings.CACHE_TTL
    loadData = await jsonLoad(filePath, ttl=load_ttl)

    # If no specific page requested, return whatever is cached (may be dict or list)
    if page is None:
        return loadData if loadData else None

    # When a page is requested, ensure it exists in cache
    if isinstance(loadData, dict) and loadData and ensure_page_exists(loadData, page):
        lastPage = loadData.get("lastPage", 1)
        pageInfo = {
            "lastPage": lastPage,
            "currentPage": page,
        }
        data = loadData["pages"][str(page)]
        return {
            "pageInfo": pageInfo,
            "data": data,
        }

    # No cache available, caller should fetch from API
    return None


async def saveCacheData(pageInfo: Dict[str, Any], media: List[Dict[str, Any]], filePath: str, page: int) -> Dict[str, Any]:
    """
    Save the cache data for a given file and page.
    Returns the structured cached response dict with pageInfo and data.
    """
    structuredData = structureAnilistArray(media)

    # Cap lastPage to a sane maximum (align with pagination constraints)
    lastPage = min(pageInfo.get("lastPage", 1), 50)
    pageInfo_out = {
        "lastPage": lastPage,
        "currentPage": page,
    }

    # Persist to DB if present (lazy import to avoid test-time DB dependency)
    try:
        from app.database.addFile import findFileByName, updateInDb  # type: ignore
        findDb = await findFileByName(f"{filePath}.json")
        if findDb:
            await updateInDb(f"{filePath}.json", {"$set": {f"data.pages.{page}": structuredData}})
            logger.info(f"Updated database cache for {filePath}.json")
    except Exception as e:
        # Skip DB persistence if unavailable
        logger.warning(f"Skipped database cache update for {filePath}: {e}")

    # Persist to JSON file
    await jsonSave(filePath, page, {"lastPage": lastPage, "data": structuredData})
    return {
        "pageInfo": pageInfo_out,
        "data": structuredData,
    }
    
    