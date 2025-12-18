from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from app.helpers.fetchHelpers import make_api_request_async
import httpx
from app.queries.query_manager import query_manager
from app.helpers.response_envelope import success_response, error_response

router = APIRouter()

# Define the request model
class FYPRequest(BaseModel):
    collection: list[str]

@router.post("/fyp")
async def genres_GENRE(request: Request, fyp_request: FYPRequest, page: int = Query(1, ge=1, le=50)):
    try:
        # Extract the FYP collection from the request body
        collection = fyp_request.collection

        # Query for FYP
        query_fyp = query_manager.get_query("fyp", "get_fyp")
        result = []

        # Iterate over FYP IDs and fetch associated data
        for fyid in collection:
            main_res = await make_api_request_async({
                "query": query_fyp,
                "variables": {"id": fyid, "page": page}
            })
            
            # Validate response structure
            if main_res.get("errors"):
                return error_response(request, status_code=500, message="Request error", error=main_res["errors"])            
            
            # Extract recommendations
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
            
            
            # Append results for the current ID
            result.append({
                "id": fyid,
                "recommendations": recommendations
            })
        
        # flatten recommendations
        flattened_recommendations = [recommendation["recommendations"] for recommendation in result if recommendation.get("recommendations")]
        # flattened list
        flattened_list = [item for sublist in flattened_recommendations for item in sublist]
        
        meta = {"fyp": {"count": len(flattened_list), "ids": collection, "page": page}}
        return success_response(request, data=flattened_list, meta=meta)

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        # Handle any unforeseen errors
        return error_response(request, status_code=500, message=f"Unexpected error: {str(e)}", error=str(e))
