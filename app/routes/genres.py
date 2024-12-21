from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
import requests

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
        if genre_res.get("errors"):
            raise HTTPException(status_code=500, detail=genre_res["errors"])
        
        # Extract the genre collection
        collection = genre_res["data"]["GenreCollection"]
        
        # Query for releases by genre
        genre_item = query_manager.get_query("genre_item", "get_genre_item")
        result = []

        # Iterate over genres and fetch associated data
        for genre in collection:
            main_res = make_api_request({
                "query": genre_item,
                "variables": {"genre": genre}
            })
            
            # Validate release response structure
            if main_res.get("error"):
                raise HTTPException(status_code=500, detail=main_res["error"])
            
            # Append results
            result.append({
                "genre": genre,
                "data": main_res["data"]["Page"]["media"]
            })
        
        # Return the results
        return {"result": result}, 200

    except requests.exceptions.RequestException as e:
        # Handle request-related errors
        return {"error": f"Request error: {str(e)}"}, 500

    except Exception as e:
        # Handle any unforeseen errors
        return {"error": f"Unexpected error: {str(e)}"}, 500
