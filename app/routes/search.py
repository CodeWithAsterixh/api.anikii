from fastapi import APIRouter
import requests
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager

router = APIRouter()

@router.get("/search")
def search(keyword: str):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("search", "search_media")        
        # Define the variables
        variables = {"search": keyword}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)  # Assuming make_api_request returns a response object

        # Check for errors in the response
        if response.get("errors"):
            return {"error": response["errors"]}, 500
        
        data = response["data"]["Page"]["media"]

        # Return the parsed result as JSON
        return data, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
