from fastapi import APIRouter, Path, Query, Request, HTTPException
from typing import Optional
from urllib.parse import urlparse
from app.services.stream_resolver_service import get_episode_stream
from app.services.stream_proxy_service import stream_video_content
from app.helpers.scrapers.mp4Up import getVid
from app.helpers.response_envelope import error_response
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/anime", tags=["stream-actions"])

@router.get("/{id}/stream/ep/{ep}/download")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def download_episode(
    request: Request,
    id: int = Path(..., ge=1),
    ep: int = Path(..., ge=1),
    type: str = Query("sub", regex="^(sub|dub)$")
):
    """Proxy download for an episode via mp4upload."""
    try:
        episode_data = await get_episode_stream(id, ep, type)
        mp4_link = None
        links = episode_data.get("stream_links", [])
        for link in links:
            if isinstance(link, dict):
                if link.get("name") == "mp4upload":
                    mp4_link = link.get("url")
                    break
            elif getattr(link, "name", None) == "mp4upload":
                mp4_link = getattr(link, "url", None)
                break
        
        if not mp4_link:
             raise HTTPException(status_code=404, detail="mp4upload link not found")
        
        video_url = await getVid(mp4_link)
        if not video_url:
             raise HTTPException(status_code=500, detail="Failed to extract video URL")
        
        title = episode_data.get("episode_info", {}).get("title", f"anime_{id}_ep_{ep}")
        return await stream_video_content(video_url, mp4_link, title)
    except HTTPException as e:
        return error_response(request, status_code=e.status_code, message=e.detail)
    except Exception as e:
        return error_response(request, status_code=500, message="Download failed", error=str(e))

@router.get("/{id}/stream/ep/{ep}/download-direct")
async def download_direct_stream(
    request: Request,
    id: int = Path(..., ge=1),
    ep: int = Path(..., ge=1),
    type: str = Query("sub", regex="^(sub|dub)$"),
    provider: Optional[str] = Query(None),
    disable_ssl: bool = Query(False)
):
    """Download direct stream with optional provider override."""
    try:
        episode_data = await get_episode_stream(id, ep, type, provider)
        
        # Try direct link first
        direct_link = next((link["url"] for link in episode_data.get("stream_links", []) if isinstance(link, dict) and link.get("name") == "direct"), None)
        if not direct_link:
            direct_link = next((getattr(link, "url", None) for link in episode_data.get("stream_links", []) if getattr(link, "name", None) == "direct"), None)

        title = episode_data.get("episode_info", {}).get("title", f"anime_{id}_ep_{ep}")

        if direct_link:
            referer = ""
            try:
                u = urlparse(direct_link)
                if u.scheme and u.netloc:
                    referer = f"{u.scheme}://{u.netloc}/"
            except:
                pass
            return await stream_video_content(direct_link, referer, title, disable_ssl=disable_ssl)

        # Fallback to mp4upload
        mp4_link = next((link["url"] for link in episode_data.get("stream_links", []) if isinstance(link, dict) and link.get("name") == "mp4upload"), None)
        if not mp4_link:
            mp4_link = next((getattr(link, "url", None) for link in episode_data.get("stream_links", []) if getattr(link, "name", None) == "mp4upload"), None)

        if not mp4_link:
            raise HTTPException(status_code=404, detail="No suitable stream link found")

        video_url = await getVid(mp4_link)
        if not video_url:
            raise HTTPException(status_code=500, detail="Failed to extract video URL")

        return await stream_video_content(video_url, mp4_link, title, disable_ssl=disable_ssl)
    except HTTPException as e:
        return error_response(request, status_code=e.status_code, message=e.detail)
    except Exception as e:
        return error_response(request, status_code=500, message="Direct download failed", error=str(e))

@router.get("/{id}/stream/ep/{ep}/live")
async def live_stream(
    request: Request,
    id: int = Path(..., ge=1),
    ep: int = Path(..., ge=1),
    type: str = Query("sub", regex="^(sub|dub)$"),
    provider: Optional[str] = Query(None)
):
    """Live streaming endpoint (proxied)."""
    try:
        episode_data = await get_episode_stream(id, ep, type, provider)
        mp4_link = next((link["url"] for link in episode_data.get("stream_links", []) if isinstance(link, dict) and link.get("name") == "mp4upload"), None)
        if not mp4_link:
            mp4_link = next((getattr(link, "url", None) for link in episode_data.get("stream_links", []) if getattr(link, "name", None) == "mp4upload"), None)

        if not mp4_link:
            raise HTTPException(status_code=404, detail="mp4upload link not found")

        video_url = await getVid(mp4_link)
        if not video_url:
            raise HTTPException(status_code=500, detail="Failed to extract video URL")

        return await stream_video_content(video_url, mp4_link, f"live_{id}_{ep}", content_type="application/octet-stream")
    except HTTPException as e:
        return error_response(request, status_code=e.status_code, message=e.detail)
    except Exception as e:
        return error_response(request, status_code=500, message="Live stream failed", error=str(e))
