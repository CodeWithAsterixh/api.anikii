from fastapi import APIRouter,HTTPException, Request
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.structure.details import structureAnilistCharacters
import requests
from app.helpers.response_envelope import success_response, error_response


router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/characters")
def characters(request: Request, id:int, page:int=1):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("characters", "get_characters")        
        # Define the variables
        variables = {"id": id,"page": page}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)
        if response.get("errors"):
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])
        
        pageInfo = response["data"]["Media"]["characters"]["pageInfo"]
        characters = response["data"]["Media"]["characters"]["edges"]
        ch = structureAnilistCharacters(characters)
        result = {
            "pageInfo": pageInfo,
            "characters": ch
        }
        meta = {"pagination": pageInfo}
        return success_response(request, data=result, meta=meta)

    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))

