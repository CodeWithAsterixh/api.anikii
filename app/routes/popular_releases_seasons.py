from fastapi import APIRouter, Request
import httpx
from app.helpers.fetchHelpers import make_api_request_async
from app.helpers.timeFunction import this_when, get_current_season
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import runCacheData,saveCacheData
from app.helpers.response_envelope import success_response, error_response

router = APIRouter()

@router.get("/popular/releases/seasons")
async def popular_releases_seasons(request: Request, page: int=1):
    try:
        cacheDataAvailable = runCacheData(page,"popular_releases_seasons")
        if cacheDataAvailable:
            meta = {"pagination": cacheDataAvailable.get("pageInfo")}
            return success_response(request, data=cacheDataAvailable.get("data"), meta=meta)
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
        response = await make_api_request_async(body)

        # Check for errors in the response
        if response.get("errors"):
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])

        media = response["data"]["Page"]["media"]
        pageInfo = response["data"]["Page"]["pageInfo"]
        
        data = saveCacheData(pageInfo, media, "popular_releases_seasons", page)
        meta = {"pagination": pageInfo}
        return success_response(request, data=media, meta=meta)

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
