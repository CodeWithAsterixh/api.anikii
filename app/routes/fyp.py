from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager

router = APIRouter()

# Define the request model
class FYPRequest(BaseModel):
    collection: list[str]

@router.post("/fyp")
def genres_GENRE(fyp_request: FYPRequest, page:int=1):
    try:
        # Extract the FYP collection from the request body
        collection = fyp_request.collection

        # Query for FYP
        query_fyp = query_manager.get_query("fyp", "get_fyp")
        result = []

        # Iterate over FYP IDs and fetch associated data
        for fyid in collection:
            main_res = make_api_request({
                "query": query_fyp,
                "variables": {"id": fyid, "page":page}
            })
            
            # Validate response structure
            if main_res.get("errors"):
                raise HTTPException(status_code=500, detail=main_res["errors"])
            
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
        # Return the results
        return [{"result": flattened_list}, 200]

    except HTTPException as http_ex:
        # Handle HTTP-related errors
        raise http_ex

    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
