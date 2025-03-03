from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager

import requests

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/stream")
async def animeInfoStream(id: int):
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
