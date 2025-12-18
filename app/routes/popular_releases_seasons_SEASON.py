from fastapi import APIRouter, Request
from app.helpers.fetchHelpers import make_api_request
from app.helpers.timeFunction import this_when, get_current_season, available_seasons
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import runCacheData,saveCacheData
from app.helpers.response_envelope import success_response, error_response

import requests

router = APIRouter(prefix="/popular/releases/seasons", tags=["season"])

@router.get("/{season}")
def popular_releases_seasons_SEASON(request: Request, season: str, page: int=1):
    try:
        cacheDataAvailable = runCacheData(page,f"popular_releases_seasons_{season}")
        if cacheDataAvailable:
            meta = {"pagination": cacheDataAvailable.get("pageInfo")}
            return success_response(request, data=cacheDataAvailable.get("data"), meta=meta)
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
            "year": this_when.year,
        }

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)

        # Check for errors in the response
        if "errors" in response:
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])

        media = response["data"]["Page"]["media"]
        pageInfo = response["data"]["Page"]["pageInfo"]
        
        data = saveCacheData(pageInfo, media, f"popular_releases_seasons_{season}", page)
        meta = {"pagination": pageInfo}
        return success_response(request, data=media, meta=meta)

    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
