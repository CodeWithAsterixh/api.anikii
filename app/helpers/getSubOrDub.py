import requests
from fastapi import HTTPException
import urllib3

# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL

async def get_episode_data(id: int, ep: int, type: str = "sub"):
    """
    Common helper to retrieve streaming info for an episode.
    Depending on the type ("sub" or "dub"), it fetches provider data and builds
    the appropriate URL, then parses the streaming info from that URL.
    """
    try:
        provider = await fetch_malsyn_data_and_get_provider(id)
        if type == "sub":
            gogoId = provider.get("id_provider",{}).get("idGogo", None)
        elif type == "dub":
            gogoId = provider.get("id_provider",{}).get("idGogoDub", None)
        else:
            raise HTTPException(status_code=400, detail="Invalid type parameter")
        
        url = f"{BASEURL}/{gogoId}-episode-{ep}"
        # Parse the streaming info from the URL.
        if gogoId:
            data = parse_streaming_info(url)
            return data
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"{type.capitalize()} episode not found: {ep}")
        else:
            raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
