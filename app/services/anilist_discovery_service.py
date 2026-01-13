from typing import Any, Dict, List, Tuple
from app.helpers.fetchHelpers import make_api_request_async
from app.structure.listItem import structure_anilist_array
from app.queries.query_manager import query_manager

async def fetch_search(keyword: str) -> List[Dict[str, Any]]:
    """
    Fetch search results from AniList and return structured list items.
    """
    query = query_manager.get_query("search", "search_media")
    variables = {"search": keyword}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)

    if response.get("errors"):
        raise RuntimeError(response["errors"])

    data = response["data"]["Page"]["media"]
    return structure_anilist_array(data)

async def fetch_popular(page: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Fetch popular media page_info and media list from AniList.
    """
    query = query_manager.get_query("popular", "get_popular_media")
    variables = {"page": page}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)

    if response.get("errors"):
        raise RuntimeError(response["errors"])

    page_info = response["data"]["Page"]["page_info"]
    media = response["data"]["Page"]["media"]
    return page_info, media

async def fetch_genres() -> List[str]:
    """
    Fetch the genre collection from AniList.
    """
    query_genres = query_manager.get_query("genres", "get_genres")
    genre_res = await make_api_request_async({"query": query_genres, "variables": {}})

    if genre_res.get("errors"):
        raise RuntimeError(genre_res["errors"])

    return genre_res["data"]["GenreCollection"]
