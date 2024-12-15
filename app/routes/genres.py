from fastapi import APIRouter
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from typing import List

router = APIRouter()

@router.get("/genres")
def genres_GENRE():
    try:
        # Retrieve the query string for the genre collection
        query_genres = query_manager.get_query("genres", "get_genres")
        
        # Fetch genre collection
        genre_res = make_api_request({
            "query": query_genres,
            "variables": {}
        })
        
        # Validate response structure
        if not genre_res.get("data") or not genre_res["data"].get("GenreCollection"):
            return {"error": "Invalid response structure"}, 500
        
        # Extract the genre collection
        collection = genre_res["data"]["GenreCollection"]
        
        # Query for releases by genre
        query_releases = query_manager.get_query("releases", "get_releases")
        result = []

        # Iterate over genres and fetch associated data
        for genre in collection:
            main_res = make_api_request({
                "query": query_releases,
                "variables": {"genre": genre}
            })
            
            # Validate release response structure
            if not main_res.get("data") or not main_res["data"].get("Page"):
                return {"error": f"Invalid response structure for genre: {genre}"}, 500
            
            # Append results
            result.append({
                "genre": genre,
                "data": main_res
            })
        
        # Return the results
        return {"result": result}, 200

    except requests.exceptions.RequestException as e:
        # Handle request-related errors
        return {"error": f"Request error: {str(e)}"}, 500

    except Exception as e:
        # Handle any unforeseen errors
        return {"error": f"Unexpected error: {str(e)}"}, 500
