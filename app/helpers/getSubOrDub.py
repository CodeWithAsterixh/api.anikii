import requests
from fastapi import HTTPException
import urllib3
from app.helpers.getEpM3u8BasedGogo import get_episode


# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL, slugify_anikii

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
            # Build a 9anime.org.lv episode URL using the anime title slug
            anime_title = data.anime_info.get("title") if isinstance(data.anime_info, dict) else None
            slug = slugify_anikii(anime_title) if anime_title else None
            nineanime_base = "https://9anime.org.lv"
            if slug:
                nineanime_url = (
                    f"{nineanime_base}/{slug}-dub-episode-{ep}" if type == "dub" else f"{nineanime_base}/{slug}-episode-{ep}"
                )
            else:
                nineanime_url = None
            
            # Get extra servers info from gogo
            episode_extra = await get_episode(gogoId, ep)
            vidcdn_url = episode_extra.get("servers",{}).get("vidcdn",None)

            # Post-process parsed links:
            # - remove any with null/empty url
            # - disable gogoanime.me.uk newplayer hd-1/hd-2 entries
            # - ensure //vidmoly.net URLs have https prefix
            # - strip wrapping backticks/quotes/whitespace
            processed_links = []
            for link in data.stream_links:
                if isinstance(link, dict):
                    name_val = link.get("name")
                    url_val = link.get("url")
                else:
                    name_val = getattr(link, "name", None)
                    url_val = getattr(link, "url", None)
                # Remove null/empty
                if not url_val:
                    continue
                # Normalize formatting artifacts
                if isinstance(url_val, str):
                    url_val = url_val.strip().strip("`").strip('"').strip("'")
                # Ensure protocol prefix for protocol-relative URLs
                if isinstance(url_val, str) and url_val.startswith("//"):
                    url_val = "https:" + url_val
                # Disable specific gogoanime hd-1/hd-2 player links
                if (
                    name_val == "anime"
                    and isinstance(url_val, str)
                    and "gogoanime.me.uk/newplayer.php" in url_val
                    and ("type=hd-1" in url_val or "type=hd-2" in url_val)
                ):
                    continue
                processed_links.append({"name": name_val, "url": url_val})
            
            # Build final stream_links list
            stream_links = [
                *processed_links,
            ]
            if vidcdn_url:
                stream_links.append({"name":"vidcdn", "url": vidcdn_url})
            if nineanime_url:
                stream_links.append({"name":"9anime", "url": nineanime_url})
            
            return {
                "anime_info":data.anime_info,
                "episode_info":data.episode_info,
                "stream_links":stream_links,
            }
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
