from typing import Any, Dict, List
from app.helpers.fetchHelpers import make_api_request_async
from app.structure.listItem import structure_anilist_item
from app.structure.anime_details import structure_anilist_relations, structure_anilist_trailer
from app.structure.character_details import structure_anilist_characters
from app.queries.query_manager import query_manager

async def fetch_anime_details(id: int) -> Dict[str, Any]:
    """Fetch raw anime details Media object from AniList."""
    query = query_manager.get_query("description", "get_descriptions")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    return response["data"]["Media"]

async def fetch_anime_relations(id: int) -> List[Dict[str, Any]]:
    """Fetch and structure anime relations for a given id."""
    query = query_manager.get_query("relations", "get_relations")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    data = response["data"]["Media"]
    return structure_anilist_relations({"data": data})

async def fetch_trailers(id: int) -> Dict[str, Any]:
    """Fetch and structure trailer info for a given anime id."""
    query = query_manager.get_query("trailers", "get_trailers")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    data = response["data"]["Media"]
    return structure_anilist_trailer(data)

async def fetch_recommended(id: int, page: int = 1) -> Dict[str, Any]:
    """Fetch recommendations for an anime, returning page_info and structured items."""
    query = query_manager.get_query("recommended", "get_recommended")
    variables = {"id": id, "page": page}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    media = response["data"]["Media"]
    nodes = media["recommendations"]["nodes"]
    page_info = media["recommendations"]["page_info"]
    nodes_array: List[Dict[str, Any]] = []
    for node in nodes:
        rec_media = node.get("mediaRecommendation")
        if rec_media:
            structure_data = structure_anilist_item(rec_media)
            nodes_array.append(structure_data)
    return {"page_info": page_info, "recommendations": nodes_array}

async def fetch_characters(id: int) -> List[Dict[str, Any]]:
    """Fetch and structure characters for an anime."""
    query = query_manager.get_query("characters", "get_characters")
    variables = {"id": id}
    body = {"query": query, "variables": variables}
    response = await make_api_request_async(body)
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    edges = response["data"]["Media"]["characters"]["edges"]
    return structure_anilist_characters(edges)
