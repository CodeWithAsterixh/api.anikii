from fastapi import APIRouter
import requests
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
router = APIRouter()

@router.get("/popular/upcoming")
def popular_releases(page: int=1):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("upcoming", "get_upcoming") 
        # Define the variables
        variables = {"page": page}

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
        
        pageInfo = response["data"]["Page"]["pageInfo"]
        media = [item['media'] for item in response["data"]["Page"]["airingSchedules"] if 'media' in item]

        # Return the parsed result as JSON
        return {"result": {
            "pageInfo":pageInfo,
            "media":media
            }}, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
