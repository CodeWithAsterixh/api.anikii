from fastapi import APIRouter, HTTPException, Request
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager

import requests
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/stream")
async def animeInfoStream(request: Request, id: int):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("stream", "get_stream_data")
        
        # Define the variables
        variables = {"id": id}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)
        if response.get("errors"):
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])
        data = response["data"]["Media"]
        
        return success_response(request, data=data)

    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
