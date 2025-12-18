from fastapi import APIRouter, Request
import requests
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.json.cacheData import runCacheData,saveCacheData
from app.helpers.response_envelope import success_response, error_response

router = APIRouter()

@router.get("/popular/upcoming")
def popular_upcoming(request: Request, page: int=1):
    try:
        cacheDataAvailable = runCacheData(page,"popular_upcoming")
        if cacheDataAvailable:
            meta = {"pagination": cacheDataAvailable.get("pageInfo")}
            return success_response(request, data=cacheDataAvailable.get("data"), meta=meta)
        # Retrieve the query string using the query manager
        query = query_manager.get_query("upcoming", "get_upcoming") 
        # Define the variables
        variables = {"page": page}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)
        # Check for errors in the response
        if response.get("errors"):
            return error_response(request, status_code=500, message="AniList error", error=response["errors"])
        
        media = [item['media'] for item in response["data"]["Page"]["airingSchedules"] if 'media' in item]
        pageInfo = response["data"]["Page"]["pageInfo"]
        
        data = saveCacheData(pageInfo, media, "popular_upcoming", page)
        meta = {"pagination": pageInfo}
        return success_response(request, data=media, meta=meta)


    except requests.exceptions.RequestException as e:
        return error_response(request, status_code=500, message="Request error", error=str(e))

    except Exception as e:
        return error_response(request, status_code=500, message="Unexpected error", error=str(e))
