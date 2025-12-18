from typing import Any, Dict, List, Tuple
from app.helpers.fetchHelpers import make_api_request_async
from app.structure.listItem import structureAnilistArray, structureAnilistItem
from app.structure.details import structureAnilistRelations, structureAnilistTrailer
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
        # Let the caller decide how to handle errors
        raise RuntimeError(response["errors"])  # includes AniList GraphQL errors

    data = response["data"]["Page"]["media"]
    return structureAnilistArray(data)

async def fetch_popular(page: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Fetch popular media pageInfo and media list from AniList.
    Returns (pageInfo, media).
    """
    query = query_manager.get_query("popular", "get_popular_media")
    variables = {"page": page}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)

    if response.get("errors"):
        raise RuntimeError(response["errors"])  # includes AniList GraphQL errors

    pageInfo = response["data"]["Page"]["pageInfo"]
    media = response["data"]["Page"]["media"]
    return pageInfo, media

async def fetch_genres() -> List[str]:
    """
    Fetch the genre collection from AniList.
    """
    query_genres = query_manager.get_query("genres", "get_genres")
    genre_res = await make_api_request_async({"query": query_genres, "variables": {}})

    if genre_res.get("errors"):
        raise RuntimeError(genre_res["errors"])  # includes AniList GraphQL errors

    return genre_res["data"]["GenreCollection"]

async def fetch_anime_details(id: int) -> Dict[str, Any]:
    """Fetch raw anime details Media object from AniList."""
    query = query_manager.get_query("description", "get_descriptions")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])  # includes AniList GraphQL errors
    return response["data"]["Media"]

async def fetch_anime_relations(id: int) -> Dict[str, Any]:
    """Fetch and structure anime relations for a given id."""
    query = query_manager.get_query("relations", "get_relations")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])  # includes AniList GraphQL errors
    data = response["data"]["Media"]
    return structureAnilistRelations({"data": data})

async def fetch_trailers(id: int) -> Dict[str, Any]:
    """Fetch and structure trailer info for a given anime id."""
    query = query_manager.get_query("trailers", "get_trailers")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])  # includes AniList GraphQL errors
    data = response["data"]["Media"]
    return structureAnilistTrailer(data)

async def fetch_recommended(id: int, page: int = 1) -> Dict[str, Any]:
    """Fetch recommendations for an anime, returning pageInfo and structured items."""
    query = query_manager.get_query("recommended", "get_recommended")
    variables = {"id": id, "page": page}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])  # includes AniList GraphQL errors
    media = response["data"]["Media"]
    nodes = media["recommendations"]["nodes"]
    pageInfo = media["recommendations"]["pageInfo"]
    nodesArray: List[Dict[str, Any]] = []
    for node in nodes:
        structureData = structureAnilistItem(node.get("mediaRecommendation"))
        nodesArray.append(structureData)
    return {"pageInfo": pageInfo, "recommendations": nodesArray}