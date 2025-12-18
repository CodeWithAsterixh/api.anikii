from fastapi import APIRouter, Request
import httpx
from app.helpers.response_envelope import success_response, error_response
from app.helpers.fetchHelpers import make_api_request_async
from app.queries.query_manager import query_manager

router = APIRouter()

@router.get("/anime/{anime_id}/characters")
async def anime_ID_characters(request: Request, anime_id: int):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("characters", "get_characters")
        # Define the variables
        variables = {"id": anime_id}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = await make_api_request_async(body)

        # Check for errors in the response
        if response.get("errors"):
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])            
        # Extract the response data
        data = response["data"]["Media"]["characters"]["edges"]

        # Return the data using your success response handler
        return success_response(request, data=data)

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))
    
    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))

