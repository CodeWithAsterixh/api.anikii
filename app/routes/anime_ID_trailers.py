from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
import requests

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/trailers")
async def animeInfoTrailer(id: int):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("trailers", "get_trailers")
        
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
            raise HTTPException(status_code=500, detail=response["errors"])
        data = response["data"]["Media"]
        

        # Check for errors in the response
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])

        # Return the parsed result as JSON
        return data, 200

    except requests.exceptions.RequestException as e:
        # Handle any general request errors
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
