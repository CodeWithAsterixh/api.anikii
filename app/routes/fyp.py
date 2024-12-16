from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager

router = APIRouter()

# Define the request model
class FYPRequest(BaseModel):
    collection: list[str]

@router.post("/fyp")
def genres_GENRE(fyp_request: FYPRequest):
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
                "variables": {"id": fyid}
            })
            
            # Validate response structure
            if main_res.get("errors"):
                raise HTTPException(status_code=500, detail=main_res["errors"])
            
            # Extract recommendations
            media_recommendations = [
                edge["node"]["mediaRecommendation"]
                for edge in main_res["data"]["Media"]["recommendations"]["edges"]
                if edge.get("node") and edge["node"].get("mediaRecommendation")
            ]
            
            # Append results for the current ID
            result.append({
                "id": fyid,
                "recommendations": media_recommendations
            })
        
        # Return the results
        return {"result": result}

    except HTTPException as http_ex:
        # Handle HTTP-related errors
        raise http_ex

    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
