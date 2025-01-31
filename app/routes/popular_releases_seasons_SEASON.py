from fastapi import APIRouter
from app.helpers.fetchHelpers import make_api_request
from app.helpers.timeFunction import this_when, get_current_season, available_seasons
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import runCacheData,saveCacheData

import requests

router = APIRouter(prefix="/popular/releases/seasons", tags=["season"])

@router.get("/{season}")
def popular_releases_seasons_SEASON(season: str, page: int=1):
    try:
        cacheDataAvailable = runCacheData(page,f"popular_releases_seasons_{season}")
        if cacheDataAvailable:
            return cacheDataAvailable
        # Retrieve the query string using the query manager
        query = query_manager.get_query("releases", "get_releases")

        # If the provided season is invalid, use the current season
        if not any(s.lower() == season.lower() for s in available_seasons):
            season = get_current_season()

        # Ensure the season is in uppercase format
        season = season.upper()

        # Define the variables for the API request
        variables = {
            "page": page,
            "season": season,
            "year": this_when.year,  # Ensure this_when() is used to get the year
        }

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)  # Assuming make_api_request returns a response object

        # Check for errors in the response
        if "errors" in response:
            return {"error": response["errors"]}, 500

        media = response["data"]["Page"]["media"]
        pageInfo = response["data"]["Page"]["pageInfo"]
        
        data = saveCacheData(pageInfo, media, f"popular_releases_seasons_{season}", page)
        # Return the parsed result as JSON
        return data, 200

    except requests.exceptions.RequestException as e:
        # Handle request-specific errors (e.g., network, timeout)
        return {"error": f"Request error: {str(e)}"}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500
