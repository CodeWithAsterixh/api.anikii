from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
import requests
from app.helpers.json.cacheData import runCacheData
from app.helpers.json.jsonParser import jsonWrite


router = APIRouter()

@router.get("/genres")
def genres():
    try:
        cacheDataAvailable = runCacheData(None, "genres")
        if cacheDataAvailable:
            return cacheDataAvailable,200
        # Retrieve the query string for the genre collection
        query_genres = query_manager.get_query("genres", "get_genres")
        
        # Fetch genre collection
        genre_res = make_api_request({
            "query": query_genres,
            "variables": {}
        })
        
        # Validate response structure
        if genre_res.get("errors"):
            raise HTTPException(status_code=500, detail=genre_res["errors"])
        
        # Extract the genre collection
        collection = genre_res["data"]["GenreCollection"]
        # Return the results
        data = jsonWrite("genres", collection)
        return data, 200

    except requests.exceptions.RequestException as e:
        # Handle request-related errors
        return {"error": f"Request error: {str(e)}"}, 500

    except Exception as e:
        # Handle any unforeseen errors
        return {"error": f"Unexpected error: {str(e)}"}, 500
