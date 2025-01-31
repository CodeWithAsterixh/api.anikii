from fastapi import APIRouter
import requests
from app.helpers.fetchHelpers import make_api_request
from app.helpers.timeFunction import this_when, get_current_season
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import runCacheData,saveCacheData

router = APIRouter()

@router.get("/popular/releases/seasons")
def popular_releases_seasons(page: int=1):
    try:
        cacheDataAvailable = runCacheData(page,"popular_releases_seasons")
        if cacheDataAvailable:
            return cacheDataAvailable
        # Retrieve the query string using the query manager
        query = query_manager.get_query("releases", "get_releases")        
        # Define the variables
        variables = {
            "page": page,
            "season": get_current_season(),
            "year": this_when.year,
        }

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

        media = response["data"]["Page"]["media"]
        pageInfo = response["data"]["Page"]["pageInfo"]
        
        data = saveCacheData(pageInfo, media, "popular_releases_seasons", page)
        # Return the parsed result as JSON
        return data, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
