from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
import requests

router = APIRouter(prefix="/genres", tags=["genre"])


@router.get("/{genre}")
def genres_GENRE(genre:str, page: int=1):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("genre_item", "get_genre_item")        
        # Define the variables
        variables = {"genre": genre, "page":page}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)  # Assuming make_api_request returns a response object

        # Check for errors in the response
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])

        # Return the parsed result as JSON
        return {"result": response["data"]["Page"]}, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
