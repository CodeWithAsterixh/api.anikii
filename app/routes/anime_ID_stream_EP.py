import requests
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import urllib3
from app.helpers.getSubOrDub import get_episode_data

# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)


from app.helpers.scrapers.mp4Up import getVid

router = APIRouter(prefix="/anime", tags=["id", "ep"])


# Endpoint to fetch streaming info (sub/dub) for an episode.
@router.get("/{id}/stream/ep/{ep}")
async def stream_episode(id: int, ep: int, type: str = Query("sub", description="Type of episode: 'sub' or 'dub'")):
    episode_data = await get_episode_data(id, ep, type)
    return episode_data, 200

# Download endpoint that streams the original video and returns its original size.
@router.get("/{id}/stream/ep/{ep}/download")
async def download_streaming_video(id: int, ep: int, type: str = Query("sub", description="Type of episode: 'sub' or 'dub'")):
    episode_data = await get_episode_data(id, ep, type)
    if not episode_data:
        return {"error": "Episode not found"}, 404
    
    # Extract the mp4upload link from the stream_links list.
    mp4upload_link = next((link.url for link in episode_data.stream_links if link.name == "mp4upload"), None)
    if not mp4upload_link:
        raise HTTPException(status_code=404, detail="mp4upload link not found")
    
    # Use getVid to extract the direct video URL.
    video_url = await getVid(mp4upload_link)
    if not video_url:
        raise HTTPException(status_code=500, detail="Failed to extract video URL")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": mp4upload_link
    }
    
    try:
        r = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video: {e}")
    
    # Include the Content-Length header if available.
    content_length = r.headers.get("Content-Length")
    extra_headers = {"Content-Disposition": "attachment; filename=video.mp4"}
    if content_length:
        extra_headers["Content-Length"] = content_length

    def iter_content():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_content(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
        headers=extra_headers
    )

# Live streaming endpoint for an episode.
@router.get("/{id}/stream/ep/{ep}/live")
async def live_streaming_video(id: int, ep: int, type: str = Query("sub", description="Type of episode: 'sub' or 'dub'")):
    episode_data = await get_episode_data(id, ep, type)
    if not episode_data:
        return {"error": "Episode not found"}, 404
    # Extract the mp4upload link.
    mp4upload_link = next((link.url for link in episode_data.stream_links if link.name == "mp4upload"), None)
    if not mp4upload_link:
        raise HTTPException(status_code=404, detail="mp4upload link not found")
    
    video_url = await getVid(mp4upload_link)
    if not video_url:
        raise HTTPException(status_code=500, detail="Failed to extract video URL")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": mp4upload_link
    }
    
    try:
        r = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live stream: {e}")
    
    def iter_live():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_live(),
        media_type=r.headers.get("Content-Type", "application/octet-stream")
    )
