from fastapi import APIRouter,HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.structure.details import structureAnilistCharacters
import requests


router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/characters")
def characters(id:int, page:int=1):
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
        response = make_api_request(body)  # Assuming make_api_request returns a response object
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])
        
        pageInfo = response["data"]["Media"]["characters"]["pageInfo"]
        characters = response["data"]["Media"]["characters"]["edges"]
        # Flatten the `node` key while keeping other data
        # flattened_characters = [
        #     {
        #         **character["node"],
        #         **{k: v for k, v in character.items() if k != "node"},
        #         "name": nodes[index]["name"]
        #     }
        #     for index, character in enumerate(characters)
        #     if character.get("node")
        # ]
        # result = {
        #     "pageInfo": pageInfo,
        #     "characters": flattened_characters
        # }
        ch = structureAnilistCharacters(characters)
        result = {
            "pageInfo": pageInfo,
            "characters": ch
        }
        
        # Return the parsed result as JSON
        return result, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500

