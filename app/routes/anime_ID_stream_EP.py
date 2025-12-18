import logging
import re
from typing import Optional
from urllib.parse import urlparse

import urllib3
# Removed direct anime_downloader import to enforce separation of concerns
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from app.helpers.getSubOrDub import get_episode_data
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.scrapers.mp4Up import getVid
from app.services.anilist_service import fetch_anime_details
from app.services.anime_downloader_service import resolve_stream_with_anime_downloader
from app.helpers.response_envelope import success_response, error_response
import httpx

# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/anime", tags=["id", "ep"])


# Endpoint to fetch streaming info (sub/dub) for an episode.
@router.get("/{id}/stream/ep/{ep}")
async def stream_episode(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
):
    try:
        episode_data = await get_episode_data(id, ep, type)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Failed to fetch episode data")
        return error_response(request, status_code=status_code, message=detail, error=str(e))
    return success_response(request, data=episode_data)


# Download endpoint that streams the original video and returns its original size.
@router.get("/{id}/stream/ep/{ep}/download")
async def download_streaming_video(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
):
    try:
        episode_data = await get_episode_data(id, ep, type)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Failed to fetch episode data")
        return error_response(request, status_code=status_code, message=detail, error=str(e))
    if not episode_data:
        return error_response(request, status_code=404, message="Episode not found")

    # Extract the mp4upload link from the stream_links list.
    mp4upload_link = next(
        (link.url for link in episode_data["stream_links"] if link.name == "mp4upload"),
        None,
    )
    if not mp4upload_link:
        return error_response(request, status_code=404, message="mp4upload link not found")

    # Use getVid to extract the direct video URL.
    video_url = await getVid(mp4upload_link)
    if not video_url:
        return error_response(request, status_code=500, message="Failed to extract video URL")

    headers = {"User-Agent": USER_AGENT, "Referer": mp4upload_link}

    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False, follow_redirects=True) as client:
            r = await client.get(video_url, headers=headers)
            r.raise_for_status()
    except Exception as e:
        return error_response(request, status_code=500, message="Error fetching video", error=str(e))

    # Include the Content-Length header if available.
    content_length = r.headers.get("Content-Length")
    extra_headers = {
        "Content-Disposition": f"attachment; filename={episode_data['episode_info']['title']}.mp4",
    }
    if content_length:
        extra_headers["Content-Length"] = content_length

    async def iter_content():
        async for chunk in r.aiter_bytes(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_content(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
        headers=extra_headers,
    )


# Download direct stream with query params
@router.get("/{id}/stream/ep/{ep}/download-direct")
async def download_direct_stream(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
    provider: Optional[str] = Query(
        None,
        description="Optional provider override: gogoanime, 9anime, animepahe, twistmoe",
    ),
    episodes: Optional[str] = Query(
        None, description="Range of episodes in format <start>:<end> (e.g., '1:5')"
    ),
    quality: Optional[str] = Query(
        "720p", description="Quality of the episode (e.g., 360p, 480p, 720p, 1080p)"
    ),
    force_download: Optional[bool] = Query(
        False, description="Force download even if file exists"
    ),
    file_format: Optional[str] = Query(None, description="Format for naming the files"),
    skip_fillers: Optional[bool] = Query(
        False, description="Skip downloading filler episodes"
    ),
    fallback_qualities: Optional[str] = Query(
        None, description="Order of fallback qualities (e.g., 480p, 360p)"
    ),
    external_downloader: Optional[str] = Query(
        None, description="Use an external downloader like aria2c"
    ),
    disable_ssl: Optional[bool] = Query(
        False, description="Disable SSL verification for the download"
    ),
):
    print("go")
    # First, try anime-downloader for a direct stream URL
    episode_data = await resolve_stream_with_anime_downloader(
        id, ep, type, provider_override=provider
    )

    if not episode_data:
        try:
            episode_data = await get_episode_data(id, ep, type)
        except Exception as e:
            status_code = getattr(e, "status_code", 500)
            detail = getattr(e, "detail", "Failed to fetch episode data")
            return error_response(request, status_code=status_code, message=detail, error=str(e))
    # If no episode data is found, raise a 404
    if not episode_data:
        logger.warning(
            f"Episode not found for id={id}, ep={ep}, type={type}, provider={provider}"
        )
        return error_response(request, status_code=404, message="Episode not found")

    # Prefer direct link resolved by anime-downloader if present
    direct_link = next(
        (
            link["url"]
            for link in episode_data.get("stream_links", [])
            if link.get("name") == "direct"
        ),
        None,
    )

    if direct_link:
        headers = {"User-Agent": USER_AGENT}
        # Add referer header from direct link origin if available
        try:
            u = urlparse(direct_link)
            if u.scheme and u.netloc:
                headers["Referer"] = f"{u.scheme}://{u.netloc}/"
        except Exception:
            pass

        # Try fetching the video file directly from the link
        try:

           async with httpx.AsyncClient(timeout=30.0, verify=not disable_ssl, follow_redirects=True) as client:
               r = await client.get(direct_link, headers=headers)
               r.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching video: {e}")
            return error_response(request, status_code=500, message="Error fetching video", error=str(e))

        # Get content length if available
        content_length = r.headers.get("Content-Length")
        extra_headers = {
            "Content-Disposition": f"attachment; filename={episode_data['episode_info']['title']}.mp4"
        }
        if content_length:
            extra_headers["Content-Length"] = content_length

        # Stream content back to the client
        def iter_content():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return StreamingResponse(
            iter_content(),
            media_type=r.headers.get("Content-Type", "application/octet-stream"),
            headers=extra_headers,
        )

    # Fallback: Use mp4upload link resolution if direct link is unavailable
    mp4upload_link = next(
        (
            link.url
            for link in episode_data["stream_links"]
            if getattr(link, "name", None) == "mp4upload"
        ),
        None,
    )
    if not mp4upload_link:
        return error_response(request, status_code=404, message="No suitable stream link found")

    # Use mp4upload helper to resolve video URL
    video_url = await getVid(mp4upload_link)
    if not video_url:
        return error_response(request, status_code=500, message="Failed to extract video URL")

    headers = {"User-Agent": USER_AGENT, "Referer": mp4upload_link}

    # Try fetching video from the resolved link
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=not disable_ssl, follow_redirects=True) as client:
            r = await client.get(video_url, headers=headers)
            r.raise_for_status()
    except Exception as e:
        return error_response(request, status_code=500, message="Error fetching video", error=str(e))


    async def iter_content():
        async for chunk in r.aiter_bytes(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_content(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
        headers=extra_headers,
    )


# Live streaming endpoint for an episode.
@router.get("/{id}/stream/ep/{ep}/live")
async def live_streaming_video(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
    provider: Optional[str] = Query(
        None,
        description="Optional provider override: gogoanime, 9anime, animepahe, twistmoe",
    ),
):
    episode_data = await resolve_stream_with_anime_downloader(
        id, ep, type, provider_override=provider
    )
    if not episode_data:
        try:
            episode_data = await get_episode_data(id, ep, type)
        except Exception as e:
            status_code = getattr(e, "status_code", 500)
            detail = getattr(e, "detail", "Failed to fetch episode data")
            return error_response(request, status_code=status_code, message=detail, error=str(e))
    if not episode_data:
        return error_response(request, status_code=404, message="Episode not found")

    # Extract the mp4upload link.
    mp4upload_link = next(
        (link.url for link in episode_data["stream_links"] if link.name == "mp4upload"),
        None,
    )
    if not mp4upload_link:
        return error_response(request, status_code=404, message="mp4upload link not found")

    video_url = await getVid(mp4upload_link)
    if not video_url:
        return error_response(request, status_code=500, message="Failed to extract video URL")

    headers = {"User-Agent": USER_AGENT, "Referer": mp4upload_link}

    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False, follow_redirects=True) as client:
            r = await client.get(video_url, headers=headers)
            r.raise_for_status()
    except Exception as e:
        return error_response(request, status_code=500, message="Error fetching live stream", error=str(e))

    async def iter_live():
        async for chunk in r.aiter_bytes(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_live(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
    )
