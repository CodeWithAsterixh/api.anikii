from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.structure.listItem import structureAnilistItem
import requests

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/recommended")
def popular(id:int, page:int=1):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("recommended", "get_recommended")        
        # Define the variables
        variables = {"id": id,"page":page}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)  # Assuming make_api_request returns a response object
        
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])
        
        media = response["data"]["Media"]
        nodes = media["recommendations"]["nodes"]
        pageInfo = media["recommendations"]["pageInfo"]
        
        
        # recommendations = structureAnilistArray(nodes)
        nodesArray = []
        for node in nodes:
            structureData = structureAnilistItem(node.get("mediaRecommendation"))
            nodesArray.append(structureData)

        
        # Return the parsed result as JSON
        return {"pageInfo":pageInfo,"recommendations":nodesArray }, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
