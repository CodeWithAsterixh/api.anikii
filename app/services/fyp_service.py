from typing import List, Dict, Any
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager

async def get_fyp_recommendations(collection: List[str], page: int = 1) -> List[Dict[str, Any]]:
    """Fetch recommendations for a collection of anime IDs."""
    query_fyp = query_manager.get_query("fyp", "get_fyp")
    result = []

    for fyid in collection:
        main_res = await make_api_request_async({
            "query": query_fyp,
            "variables": {"id": fyid, "page": page}
        })
        
        if main_res.get("errors"):
            raise RuntimeError(main_res["errors"])
        
        nodes = main_res["data"]["Media"]["recommendations"]["nodes"]
        recommendations = [
            {
                "id": node["mediaRecommendation"]["id"],
                "title": {
                    "romaji": node["mediaRecommendation"]["title"]["romaji"],
                    "english": node["mediaRecommendation"]["title"].get("english", None),
                    "native": node["mediaRecommendation"]["title"].get("native", None)
                },
                "status": node["mediaRecommendation"]["status"],
                "coverImage": {
                    "extraLarge": node["mediaRecommendation"]["coverImage"]["extraLarge"],
                    "medium": node["mediaRecommendation"]["coverImage"]["medium"]
                },
                "popularity": node["mediaRecommendation"]["popularity"]
            }
            for node in nodes if node.get("mediaRecommendation")
        ]
        
        result.append({
            "id": fyid,
            "recommendations": recommendations
        })
    
    # Flatten recommendations
    flattened_list = [item for sublist in [r["recommendations"] for r in result] for item in sublist]
    return flattened_list
